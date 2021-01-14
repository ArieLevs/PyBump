import json
import unittest
from unittest import mock
from subprocess import run, PIPE

from src.pybump import get_setup_py_install_requires, get_versions_from_requirements, identify_possible_patch, \
    is_patchable, get_pypi_package_releases, check_available_python_patches

from . import valid_setup_py, valid_setup_py_2, invalid_setup_py_1, invalid_setup_py_2


def mocked__pypi_requests(*args):
    class MockResponse:
        def __init__(self, json_data, status_code, reason='OK'):
            self.json_data = json_data
            self.status_code = status_code
            self.reason = reason

        def json(self):
            return self.json_data

    if args[0] == 'https://pypi.org/pypi/pybump/json':
        with open('test/test_content_files/pypi_mocks/pypi_pybump_api_result.json') as json_file:
            data = json.load(json_file)
        return MockResponse(data, 200)

    if args[0] == 'https://pypi.org/pypi/GitPython/json':
        with open('test/test_content_files/pypi_mocks/pypi_gitpython_api_result.json') as json_file:
            data = json.load(json_file)
        return MockResponse(data, 200)

    if args[0] == 'https://pypi.org/pypi/SOME_not_ex1st1ng_pypi_package/json':
        return MockResponse(None, 404, 'Not Found')

    return MockResponse(None, 404)


def simulate_patch_verification(file):
    """
    execute sub process to simulate real app patch-verification execution,
    :param file: string
    :return: CompletedProcess object
    """

    return run(["python", "src/pybump.py", "patch-verification", "--file", file], stdout=PIPE, stderr=PIPE)


class PyBumpPatcherTest(unittest.TestCase):

    def setUp(self):
        pass

    def test_get_setup_py_install_requires(self):
        # should return empty list since valid_setup_py missing the install_requires=[] key
        self.assertEqual(get_setup_py_install_requires(valid_setup_py), [])

        self.assertEqual(get_setup_py_install_requires(valid_setup_py_2), ['pyyaml', 'pybump==1.3.3'])

        # invalid_setup_py_1 should return empty list even when install_requires misspelled
        self.assertEqual(get_setup_py_install_requires(invalid_setup_py_1), [])

        with self.assertRaises(RuntimeError):
            get_setup_py_install_requires(invalid_setup_py_2)

    def test_get_versions_from_requirements(self):
        self.assertEqual(
            get_versions_from_requirements(['pyyaml', 'pybump==1.3.3']),
            [
                {
                    'package_name': 'pyyaml',
                    'package_version': 'latest'
                },
                {
                    'package_name': 'pybump',
                    'package_version': {'prefix': False, 'version': [1, 3, 3], 'release': '', 'metadata': ''}
                }
            ]
        )

        # test passing empty list
        self.assertEqual(
            get_versions_from_requirements([]),
            []
        )

        with self.assertRaises(TypeError):
            get_versions_from_requirements(None)
            get_versions_from_requirements('str')

    def test_identify_possible_patch(self):
        # test most simple case when version is patchable
        self.assertEqual(
            identify_possible_patch(['0.1.2', '0.1.3', '0.3.1', '0.3.2'], [0, 3, 0]),
            {'current_patch': [0, 3, 0], 'latest_patch': [0, 3, 2], 'patchable': True}
        )

        # test most simple NOT sorted list case
        self.assertEqual(
            identify_possible_patch(['0.3.2', '0.1.2', '0.1.3', '0.3.1'], [0, 3, 1]),
            {'current_patch': [0, 3, 1], 'latest_patch': [0, 3, 2], 'patchable': True}
        )

        # test most simple NOT sorted list case
        self.assertEqual(
            identify_possible_patch(['4.2.2', '0.3.8', '0.1.2', '0.1.3', '0.3.1'], [0, 3, 1]),
            {'current_patch': [0, 3, 1], 'latest_patch': [0, 3, 8], 'patchable': True}
        )

        # test simple list case with
        self.assertEqual(
            identify_possible_patch(['0.3.2', 'text', None], [0, 3, 1]),
            {'current_patch': [0, 3, 1], 'latest_patch': [0, 3, 2], 'patchable': True}
        )

        # pass both empty lists
        with self.assertRaises(ValueError):
            identify_possible_patch([], [])

        # test version that is already latest
        self.assertEqual(
            identify_possible_patch(['0.1.2', '0.1.3', '0.3.1', '0.3.2'], [0, 3, 2]),
            {'current_patch': [0, 3, 2], 'latest_patch': [0, 3, 2], 'patchable': False}
        )

        # test not patchable version
        self.assertEqual(
            identify_possible_patch(['0.1.2', '0.1.3', '0.3.1', '0.3.2'], [0, 4, 2]),
            {'current_patch': [0, 4, 2], 'latest_patch': [0, 4, 2], 'patchable': False}
        )

    def test_is_patchable(self):
        self.assertTrue(is_patchable([0, 4, 5], [0, 4, 1]))
        self.assertFalse(is_patchable([2, 1, 2], [2, 4, 2]))
        self.assertFalse(is_patchable([0, 4, 5], [0, 4, 6]))
        self.assertFalse(is_patchable([0, 0, 1], [0, 0, 1]))

    @mock.patch('requests.get', side_effect=mocked__pypi_requests)
    def test_get_pypi_package_releases(self, mock_get):
        # mock request to https://pypi.org/pypi/pybump/json
        json_data = get_pypi_package_releases('pybump')

        with open('test/test_content_files/pypi_mocks/pypi_pybump_api_result.json') as json_file:
            data = json.load(json_file)
        self.assertEqual(json_data, data)

        # test request to https://pypi.org/pypi/SOME_not_ex1st1ng_pypi_package/json
        from requests.exceptions import RequestException
        with self.assertRaises(RequestException):
            get_pypi_package_releases('SOME_not_ex1st1ng_pypi_package')

        # make sure we mocked 3 tests
        self.assertEqual(len(mock_get.call_args_list), 2)

    @mock.patch('requests.get', side_effect=mocked__pypi_requests)
    def test_check_available_python_patches(self, mock_get):
        # the test_valid_setup.py file contains 2 dependencies
        with open('test/test_content_files/test_valid_setup.py') as py_content:
            setup_py_content = py_content.read()
        self.assertEqual(
            check_available_python_patches(setup_py_content),
            [
                {'package_name': 'pybump',
                 'version': {'current_patch': [1, 3, 1], 'latest_patch': [1, 3, 8], 'patchable': True}},
                {'package_name': 'GitPython',
                 'version': {'current_patch': [3, 1, 7], 'latest_patch': [3, 1, 12], 'patchable': True}}
            ])

        # make sure we mocked 1 tests
        self.assertEqual(len(mock_get.call_args_list), 2)


if __name__ == '__main__':
    unittest.main()
