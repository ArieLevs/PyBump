import unittest

from src.pybump import get_setup_py_install_requires, get_versions_from_requirements, identify_possible_patch, \
    is_patchable

from . import valid_setup_py, valid_setup_py_2, invalid_setup_py_1, invalid_setup_py_2


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


if __name__ == '__main__':
    unittest.main()
