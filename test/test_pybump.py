import unittest

from src.pybump import PybumpVersion, get_setup_py_version, set_setup_py_version, \
    is_semantic_string, is_valid_helm_chart, \
    write_version_to_file, read_version_from_file

from . import valid_helm_chart, invalid_helm_chart, empty_helm_chart, \
    valid_setup_py, invalid_setup_py_1, invalid_setup_py_2, \
    valid_version_file_1, valid_version_file_2, invalid_version_file_1, invalid_version_file_2


class PyBumpTest(unittest.TestCase):

    def setUp(self):
        self.version_a = PybumpVersion('9.0.7-release-text+meta.text')
        self.version_b = PybumpVersion('v1.2.3')
        self.version_c = PybumpVersion('0.4.0+meta.text-with-some-num-123123')

        # init invalid object
        self.version_d = PybumpVersion('1.5.invalid')

    def test_validate_semantic_string(self):
        self.assertTrue(self.version_a.validate_semantic_string(self.version_a.__str__()))
        # update version_a with non valid metadata
        self.version_a.metadata = 'non_valid@meta$strings'
        self.assertFalse(self.version_a.validate_semantic_string(self.version_a.__str__()))

    def test_is_larger_then(self):
        self.assertTrue(self.version_a.is_larger_then(self.version_b))
        self.assertTrue(self.version_b.is_larger_then(self.version_c))
        self.assertFalse(self.version_c.is_larger_then(self.version_a))

    def test_is_valid_semantic_version(self):
        self.assertTrue(self.version_a.is_valid_semantic_version())
        self.assertFalse(self.version_d.is_valid_semantic_version())

    def test_assemble_version_string(self):
        self.assertEqual(
            self.version_a.__str__(),
            '9.0.7-release-text+meta.text'
        )
        self.assertEqual(
            self.version_b.__str__(),
            'v1.2.3'
        )
        self.assertEqual(
            self.version_c.__str__(),
            '0.4.0+meta.text-with-some-num-123123'
        )

    def test_bump_version(self):
        self.assertEqual(self.version_a.bump_version('major'), [10, 0, 0])
        self.assertEqual(self.version_a.version, [10, 0, 0])

        self.assertEqual(self.version_b.bump_version('patch'), [1, 2, 4])
        self.assertEqual(self.version_b.bump_version('patch'), [1, 2, 5])
        self.assertEqual(self.version_b.bump_version('minor'), [1, 3, 0])
        self.assertEqual(self.version_b.bump_version('major'), [2, 0, 0])
        self.assertEqual(self.version_b.version, [2, 0, 0])

        self.assertRaises(ValueError, self.version_b.bump_version, None)
        self.assertRaises(ValueError, self.version_b.bump_version, 'not_patch')

    def test_is_semantic_string(self):
        self.assertEqual(is_semantic_string('1.2.3'),
                         {'prefix': False, 'version': [1, 2, 3], 'release': '', 'metadata': ''})
        self.assertEqual(is_semantic_string('v1.2.3'),
                         {'prefix': True, 'version': [1, 2, 3], 'release': '', 'metadata': ''})
        self.assertEqual(is_semantic_string('1.2.6-dev'),
                         {'prefix': False, 'version': [1, 2, 6], 'release': 'dev', 'metadata': ''})
        self.assertEqual(
            is_semantic_string('1.2.6-dev+some.metadata'),
            {'prefix': False, 'version': [1, 2, 6], 'release': 'dev', 'metadata': 'some.metadata'}
        )
        self.assertEqual(
            is_semantic_string('1.2.3+meta-only'),
            {'prefix': False, 'version': [1, 2, 3], 'release': '', 'metadata': 'meta-only'}
        )
        self.assertEqual(
            is_semantic_string('v1.2.3+meta-only'),
            {'prefix': True, 'version': [1, 2, 3], 'release': '', 'metadata': 'meta-only'}
        )
        self.assertNotEqual(is_semantic_string('1.2.3'),
                            {'prefix': False, 'version': [1, 2, 4], 'release': '', 'metadata': ''})
        self.assertNotEqual(
            is_semantic_string('1.2.3-ALPHA'),
            {'prefix': False, 'version': [1, 2, 3], 'release': '', 'metadata': 'ALPHA'}
        )
        self.assertNotEqual(
            is_semantic_string('1.2.3+META.ONLY'),
            {'prefix': False, 'version': [1, 2, 3], 'release': 'META.ONLY', 'metadata': ''}
        )
        self.assertTrue(is_semantic_string('0.0.0'))
        self.assertTrue(is_semantic_string('v0.0.0'))
        self.assertTrue(is_semantic_string('v1.0.11111111111111111111111111111111111111111111111'))
        self.assertTrue(is_semantic_string('13.0.75'))
        self.assertTrue(is_semantic_string('0.5.447'))
        self.assertTrue(is_semantic_string('3.0.1-alpha'))
        self.assertTrue(is_semantic_string('v3.0.1-alpha'))
        self.assertTrue(is_semantic_string('1.1.6-alpha-beta-gama'))
        self.assertTrue(is_semantic_string('0.5.0-alpha+meta-data.is-ok'))
        self.assertFalse(is_semantic_string(''))
        self.assertFalse(is_semantic_string('   '))
        self.assertFalse(is_semantic_string('1.02.3'))
        self.assertFalse(is_semantic_string('000.000.111'))
        self.assertFalse(is_semantic_string('1.2.c'))
        self.assertFalse(is_semantic_string('V1.40.2'))
        self.assertFalse(is_semantic_string('v1.2.3.4'))
        self.assertFalse(is_semantic_string('X-1.40.2'))
        self.assertFalse(is_semantic_string('1.2.-3'))
        self.assertFalse(is_semantic_string('1.9'))
        self.assertFalse(is_semantic_string('text'))

        self.assertFalse(is_semantic_string(4))
        self.assertFalse(is_semantic_string(True))
        self.assertFalse(is_semantic_string(None))

    def test_is_valid_helm_chart(self):
        self.assertTrue(is_valid_helm_chart(valid_helm_chart))
        self.assertFalse(is_valid_helm_chart(invalid_helm_chart))
        self.assertFalse(is_valid_helm_chart(empty_helm_chart))

    def test_get_setup_py_version(self):
        self.assertEqual(get_setup_py_version(valid_setup_py), '0.1.3')

        with self.assertRaises(RuntimeError):
            get_setup_py_version(invalid_setup_py_1)

        with self.assertRaises(RuntimeError):
            get_setup_py_version(invalid_setup_py_2)

    def test_set_setup_py_version(self):
        # test the version replacement string, in a content
        content_pre = 'some text before version="3.17.5", and some text after'
        # above content should be equal to below after sending to 'set_setup_py_version'
        content_post = 'some text before version="0.1.3", and some text after'

        self.assertEqual(
            set_setup_py_version(version='0.1.3', content=content_pre), content_post
        )

    def test_is_valid_version_file(self):
        self.assertTrue(is_semantic_string(valid_version_file_1))
        self.assertTrue(is_semantic_string(valid_version_file_2))
        self.assertFalse(is_semantic_string(invalid_version_file_1))
        self.assertFalse(is_semantic_string(invalid_version_file_2))
        self.assertEqual(is_semantic_string(valid_version_file_1),
                         {'prefix': False, 'version': [0, 12, 4], 'release': '', 'metadata': ''})
        self.assertEqual(is_semantic_string(valid_version_file_2),
                         {'prefix': False, 'version': [1, 5, 0], 'release': 'alpha', 'metadata': 'meta'})

    def test_write_read_files(self):
        # write_version_to_file will write any text to a given file,
        # but later when reading data from files, they will be validated.

        write_version_to_file(file_path='test_write_read_file_1.yaml',
                              file_content={'apiVersion': 'v1',
                                            'appVersion': '2.0.3',
                                            'name': 'test',
                                            'version': '0.1.0'},
                              version='1.1.2', app_version=False)
        # write same content with app_version=True
        write_version_to_file(file_path='test_write_read_file_2.yaml',
                              file_content={'apiVersion': 'v1',
                                            'appVersion': '2.0.3',
                                            'name': 'test',
                                            'version': '0.1.0'},
                              version='1.1.2', app_version=True)

        write_version_to_file(file_path='test_write_read_file.py',
                              file_content='some text before version="0.17.5", and some text after',
                              version='1.1.2', app_version=False)
        write_version_to_file(file_path='VERSION',
                              file_content='',
                              version='1.1.2', app_version=False)
        write_version_to_file(file_path='unknown.extension',
                              file_content='some version="" here',
                              version='1.1.2', app_version=False)

        self.assertEqual(read_version_from_file(
            file_path='test_write_read_file_1.yaml', app_version=False),
            {'file_content': {'apiVersion': 'v1',
                              'appVersion': '2.0.3',
                              'name': 'test',
                              'version': '1.1.2'},
             'version': '1.1.2',
             'file_type': 'helm_chart'}
        )

        self.assertEqual(read_version_from_file(
            file_path='test_write_read_file_2.yaml', app_version=True),
            {'file_content': {'apiVersion': 'v1',
                              'appVersion': '1.1.2',
                              'name': 'test',
                              'version': '0.1.0'},
             'version': '1.1.2',
             'file_type': 'helm_chart'}
        )

        self.assertEqual(read_version_from_file(
            file_path='test_write_read_file.py', app_version=False),
            {'file_content': 'some text before version="1.1.2", and some text after',
             'version': '1.1.2',
             'file_type': 'python'}
        )

        self.assertEqual(read_version_from_file(
            file_path='VERSION', app_version=False),
            {'file_content': None,
             'version': '1.1.2',
             'file_type': 'plain_version'}
        )


if __name__ == '__main__':
    unittest.main()
