import unittest

from pybump.pybump import get_setup_py_install_requires

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


if __name__ == '__main__':
    unittest.main()
