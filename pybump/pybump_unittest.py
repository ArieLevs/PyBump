import unittest
from pybump.pybump import is_semantic_string, is_valid_helm_chart, bump_version

valid_helm_chart = {'apiVersion': 'v1',
                    'appVersion': '1.0',
                    'description': 'A Helm chart for Kubernetes',
                    'name': 'test',
                    'version': '0.1.0'}
invalid_helm_chart = {'apiVersion': 'v1',
                      'notAppVersionKeyHere': '1.0',
                      'description': 'A Helm chart for Kubernetes',
                      'name': 'test',
                      'version': '0.1.0'}
empty_helm_chart = {}


class PyBumpTest(unittest.TestCase):

    def setUp(self):
        pass

    def test_is_semantic_string(self):
        self.assertEqual(is_semantic_string('1.2.3'), [1, 2, 3])
        self.assertNotEqual(is_semantic_string('1.2.3'), [1, 2, 4])
        self.assertTrue(is_semantic_string('0.0.0'))
        self.assertTrue(is_semantic_string('13.0.75'))
        self.assertTrue(is_semantic_string('0.5.447'))
        self.assertTrue(is_semantic_string('1.02.3'))
        self.assertTrue(is_semantic_string('000.000.111'))
        self.assertFalse(is_semantic_string('1.2.c'))
        self.assertFalse(is_semantic_string('1.2.-3'))
        self.assertFalse(is_semantic_string('1.2.3-dev'))
        self.assertFalse(is_semantic_string('1.9'))
        self.assertFalse(is_semantic_string('text'))

    def test_is_valid_helm_chart(self):
        self.assertTrue(is_valid_helm_chart(valid_helm_chart))
        self.assertFalse(is_valid_helm_chart(invalid_helm_chart))
        self.assertFalse(is_valid_helm_chart(empty_helm_chart))

    def test_bump_version(self):
        self.assertEqual(bump_version([9, 0, 7], 'major'), [10, 0, 0])
        self.assertEqual(bump_version([1, 2, 3], 'major'), [2, 0, 0])
        self.assertEqual(bump_version([1, 2, 3], 'minor'), [1, 3, 0])
        self.assertEqual(bump_version([1, 2, 3], 'patch'), [1, 2, 4])
        self.assertEqual(bump_version([0, 0, 9], 'patch'), [0, 0, 10])


if __name__ == '__main__':
    unittest.main()
