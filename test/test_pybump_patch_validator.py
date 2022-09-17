# import json
# import unittest
# from unittest import mock
#
# from src.pybump import PybumpVersion
# from src.pybump_patch import get_setup_py_install_requires, get_versions_from_requirements, \
#     get_pypi_package_releases, check_available_python_patches, PybumpPatchableVersion
#
# from . import valid_setup_py, valid_setup_py_2, invalid_setup_py_1, invalid_setup_py_2
#
#
# def mocked__pypi_requests(*args):
#     class MockResponse:
#         def __init__(self, json_data, status_code, reason='OK'):
#             self.json_data = json_data
#             self.status_code = status_code
#             self.reason = reason
#
#         def json(self):
#             return self.json_data
#
#     if args[0] == 'https://pypi.org/pypi/pybump/json':
#         with open('test/test_content_files/pypi_mocks/pypi_pybump_api_result.json') as json_file:
#             data = json.load(json_file)
#         return MockResponse(data, 200)
#
#     if args[0] == 'https://pypi.org/pypi/GitPython/json':
#         with open('test/test_content_files/pypi_mocks/pypi_gitpython_api_result.json') as json_file:
#             data = json.load(json_file)
#         return MockResponse(data, 200)
#
#     if args[0] == 'https://pypi.org/pypi/package_b/json':
#         with open('test/test_content_files/pypi_mocks/pypi_pybump_api_result.json') as json_file:
#             data = json.load(json_file)
#         return MockResponse(data, 200)
#
#     if args[0] == 'https://pypi.org/pypi/SOME_not_ex1st1ng_pypi_package/json':
#         return MockResponse(None, 404, 'Not Found')
#
#     return MockResponse(None, 404)
#
#
# class PyBumpPatcherTest(unittest.TestCase):
#
#     def setUp(self):
#         version_invalid_1 = PybumpVersion('latest')
#         version_invalid_2 = PybumpVersion('some_text>=more_text')
#
#         self.version_0_3_0 = PybumpVersion('0.3.0')
#         self.version_0_3_1 = PybumpVersion('v0.3.1')
#         self.version_0_3_2 = PybumpVersion('0.3.2')
#         self.version_0_3_8 = PybumpVersion('0.3.8')
#         self.version_0_4_2 = PybumpVersion('0.4.2')
#         self.version_1_3_3 = PybumpVersion('1.3.3')
#
#         self.package_a_0_3_0 = PybumpPatchableVersion('package_a', self.version_0_3_0)
#         self.package_b_0_3_1 = PybumpPatchableVersion('package_b', self.version_0_3_1)
#         self.package_c_0_3_2 = PybumpPatchableVersion('package_b', self.version_0_3_2)
#         self.package_d_0_4_2 = PybumpPatchableVersion('package_c', self.version_0_4_2)
#         self.package_invalid_a = PybumpPatchableVersion('package_invalid_a', version_invalid_1)
#         self.package_invalid_b = PybumpPatchableVersion('package_invalid_b', version_invalid_2)
#
#     def test_get_dict(self):
#         self.assertEqual(self.package_a_0_3_0.get_dict(),
#                          {'latest_patch': 'None',
#                           'package_name': 'package_a',
#                           'patchable': False,
#                           'version': '0.3.0'})
#         self.assertEqual(self.package_invalid_a.get_dict(),
#                          {'latest_patch': 'None',
#                           'package_name': 'package_invalid_a',
#                           'patchable': False,
#                           'version': '0.0.0'})
#
#     def test_str(self):
#         self.assertEqual(
#             str(self.package_a_0_3_0),
#             "{'package_name': 'package_a', 'version': '0.3.0', 'patchable': False, 'latest_patch': 'None'}")
#         self.assertEqual(
#             str(self.package_invalid_a),
#             "{'package_name': 'package_invalid_a', 'version': '0.0.0', 'patchable': False, 'latest_patch': 'None'}")
#
#     def test_get_setup_py_install_requires(self):
#         # should return empty list since valid_setup_py missing the install_requires=[] key
#         self.assertEqual(get_setup_py_install_requires(valid_setup_py), [])
#
#         self.assertEqual(get_setup_py_install_requires(valid_setup_py_2), ['pyyaml', 'pybump==1.3.3'])
#
#         # invalid_setup_py_1 should return empty list even when install_requires misspelled
#         self.assertEqual(get_setup_py_install_requires(invalid_setup_py_1), [])
#
#         with self.assertRaises(RuntimeError):
#             get_setup_py_install_requires(invalid_setup_py_2)
#
#     def test_get_versions_from_requirements(self):
#         """
#         get_versions_from_requirements function should return list of dicts in the form of:
#         [PybumpPatchableVersion, PybumpPatchableVersion, ]
#         will test against the values returned inside the PybumpVersion object
#         """
#         result = get_versions_from_requirements(
#             ['pyyaml', 'pybump==1.3.3', 'package_a >= 5.7', 'package_b~=1.1', 'package_c!=4.5.5', 'just_text=1']
#         )
#
#         # pyyaml
#         self.assertEqual(result[0].package_name, 'pyyaml')
#         self.assertEqual(result[0].version.version, [0, 0, 0])
#         self.assertEqual(result[0].version.release, None)
#         self.assertFalse(result[0].version.is_valid_semantic_version())
#
#         # pybump
#         self.assertEqual(result[1].package_name, 'pybump')
#         self.assertEqual(result[1].version.version, [1, 3, 3])
#         self.assertEqual(result[1].version.release, '')
#         self.assertTrue(result[1].version.is_valid_semantic_version())
#
#         # package_a
#         self.assertEqual(result[2].package_name, 'package_a')
#         self.assertEqual(result[2].version.version, [0, 0, 0])
#         self.assertEqual(result[2].version.release, None)
#         self.assertFalse(result[2].version.is_valid_semantic_version())
#
#         # package_b
#         self.assertEqual(result[3].package_name, 'package_b')
#         self.assertEqual(result[3].version.version, [0, 0, 0])
#         self.assertEqual(result[3].version.release, None)
#         self.assertFalse(result[3].version.is_valid_semantic_version())
#
#         # package_c
#         self.assertEqual(result[4].package_name, 'package_c!=4.5.5')
#         self.assertEqual(result[4].version.version, [0, 0, 0])
#         self.assertEqual(result[4].version.release, None)
#         self.assertFalse(result[4].version.is_valid_semantic_version())
#
#         # just_text
#         self.assertEqual(result[5].package_name, 'just_text=1')
#         self.assertEqual(result[5].version.version, [0, 0, 0])
#         self.assertEqual(result[5].version.release, None)
#         self.assertFalse(result[5].version.is_valid_semantic_version())
#
#         # test passing empty list
#         self.assertEqual(
#             get_versions_from_requirements([]),
#             []
#         )
#
#         with self.assertRaises(TypeError):
#             get_versions_from_requirements(None)
#             get_versions_from_requirements('str')
#
#     def test_identify_possible_patch(self):
#         # test package_a_0_3_0 case when version is patchable
#         self.assertFalse(self.package_a_0_3_0.patchable)
#         self.package_a_0_3_0.identify_possible_patch(['0.1.2', '0.1.3', '0.3.1', '0.3.2'])
#         self.assertTrue(self.package_a_0_3_0.patchable)
#         self.assertEqual(self.package_a_0_3_0.latest_patch.version, self.version_0_3_2.version)
#
#         # test package_b_0_3_1 NOT sorted list case
#         self.assertFalse(self.package_b_0_3_1.patchable)
#         self.package_b_0_3_1.identify_possible_patch(['0.3.2', '0.1.2', '0.1.3', '0.3.1'])
#         self.assertTrue(self.package_b_0_3_1.patchable)
#         self.assertEqual(self.package_b_0_3_1.latest_patch.version, self.version_0_3_2.version)
#
#         self.package_b_0_3_1.identify_possible_patch(['0.2.2', 'text', None])
#         self.assertFalse(self.package_b_0_3_1.patchable)
#         self.assertEqual(self.package_b_0_3_1.latest_patch.version, self.version_0_3_1.version)
#
#         # test package_b_0_3_1 NOT sorted list case
#         self.package_b_0_3_1.identify_possible_patch(['4.2.2', '0.3.8', '0.1.2', '0.1.3', '0.3.1'])
#         self.assertTrue(self.package_b_0_3_1.patchable)
#         self.assertEqual(self.package_b_0_3_1.latest_patch.version, self.version_0_3_8.version)
#
#         # pass empty list
#         with self.assertRaises(ValueError):
#             self.package_b_0_3_1.identify_possible_patch([])
#
#         # test version that is already latest
#         self.package_c_0_3_2.identify_possible_patch(['0.1.2', '0.1.3', '0.3.1', '0.3.2'])
#         self.assertFalse(self.package_c_0_3_2.patchable)
#         self.assertEqual(self.package_c_0_3_2.latest_patch.version, self.version_0_3_2.version)
#
#         # test not patchable version
#         self.package_d_0_4_2.identify_possible_patch(['4.2.2', '0.3.8', '0.1.2', '0.1.3', '0.3.1'])
#         self.assertFalse(self.package_d_0_4_2.patchable)
#         self.assertEqual(self.package_d_0_4_2.latest_patch.version, self.version_0_4_2.version)
#
#         self.assertFalse(self.package_invalid_b.patchable)
#         self.package_invalid_b.identify_possible_patch(['4.2.2', '0.3.8', '0.1.2', '0.1.3', '0.3.1'])
#         self.assertFalse(self.package_invalid_b.patchable)
#         self.assertEqual(self.package_invalid_b.latest_patch.invalid_version, 'some_text>=more_text')
#
#     def test_is_patchable(self):
#         self.assertTrue(PybumpPatchableVersion.is_patchable([0, 4, 5], [0, 4, 1]))
#         self.assertFalse(PybumpPatchableVersion.is_patchable([2, 1, 2], [2, 4, 2]))
#         self.assertFalse(PybumpPatchableVersion.is_patchable([0, 4, 5], [0, 4, 6]))
#         self.assertFalse(PybumpPatchableVersion.is_patchable([0, 0, 1], [0, 0, 1]))
#
#     @mock.patch('requests.get', side_effect=mocked__pypi_requests)
#     def test_get_pypi_package_releases(self, mock_get):
#         # mock request to https://pypi.org/pypi/pybump/json
#         json_data = get_pypi_package_releases('pybump')
#
#         with open('test/test_content_files/pypi_mocks/pypi_pybump_api_result.json') as json_file:
#             data = json.load(json_file)
#         self.assertEqual(json_data, data)
#
#         # test request to https://pypi.org/pypi/SOME_not_ex1st1ng_pypi_package/json
#         from requests.exceptions import RequestException
#         with self.assertRaises(RequestException):
#             get_pypi_package_releases('SOME_not_ex1st1ng_pypi_package')
#
#         # make sure we mocked 3 tests
#         self.assertEqual(len(mock_get.call_args_list), 2)
#
#     @mock.patch('requests.get', side_effect=mocked__pypi_requests)
#     def test_check_available_python_patches(self, mock_get):
#         # the test_valid_setup.py file contains 2 dependencies
#         with open('test/test_content_files/test_valid_setup.py') as py_content:
#             setup_py_content = py_content.read()
#             aaa = get_setup_py_install_requires(setup_py_content)
#         self.assertEqual(
#             check_available_python_patches(aaa),
#             [
#                 {'package_name': 'pybump', 'version': '1.3.1', 'patchable': True, 'latest_patch': '1.3.8'},
#                 {'package_name': 'GitPython', 'version': '3.1.7', 'patchable': True, 'latest_patch': '3.1.12'},
#             ])
#
#         # make sure we check (mocked) 2 packages
#         self.assertEqual(len(mock_get.call_args_list), 2)
#
#
# if __name__ == '__main__':
#     unittest.main()
