import unittest

from src.pybump import PybumpVersion, get_setup_py_version, set_setup_py_version, \
    is_valid_helm_chart, write_version_to_file, read_version_from_file

from . import valid_helm_chart, invalid_helm_chart, empty_helm_chart, \
    valid_setup_py, invalid_setup_py_1, invalid_setup_py_2, \
    valid_version_file_1, valid_version_file_2, invalid_version_file_1, invalid_version_file_2


class PyBumpTest(unittest.TestCase):

    def setUp(self):
        self.version_a = PybumpVersion('9.0.7-release-text+meta.text')
        self.version_b = PybumpVersion('v1.2.3')
        self.version_c = PybumpVersion('0.4.0+meta.text-with-some-num-123123')

        self.version_d = PybumpVersion('1.5.invalid')
        self.version_e = PybumpVersion('0.0.0')
        self.version_f = PybumpVersion('v0.0.0')
        self.version_g = PybumpVersion('v1.0.11111111111111111111111111111111111111111111111')
        self.version_h = PybumpVersion('13.0.75')
        self.version_i = PybumpVersion('0.5.447')
        self.version_j = PybumpVersion('v3.0.1-alpha')
        self.version_k = PybumpVersion('1.1.6-alpha-beta-gama')
        self.version_l = PybumpVersion('0.5.0-alpha+meta-data.is-ok')
        self.version_m = PybumpVersion('')
        self.version_n = PybumpVersion('      ')
        self.version_o = PybumpVersion('1.02.3')
        self.version_p = PybumpVersion('000.000.111')
        self.version_q = PybumpVersion('1.2.c')
        self.version_r = PybumpVersion('V1.40.2')
        self.version_s = PybumpVersion('v1.2.3.4')
        self.version_t = PybumpVersion('1.2.-3')
        self.version_u = PybumpVersion('1.9')
        self.version_v = PybumpVersion('text')

        self.version_x = PybumpVersion(4)
        self.version_y = PybumpVersion(True)
        self.version_z = PybumpVersion(None)

        self.valid_version_1 = PybumpVersion(valid_version_file_1)
        self.valid_version_2 = PybumpVersion(valid_version_file_2)
        self.invalid_version_1 = PybumpVersion(invalid_version_file_1)
        self.invalid_version_2 = PybumpVersion(invalid_version_file_2)

    def test_validate_semantic_string(self):
        """
        validate_semantic_string() function is called every time objects inited
        """
        self.assertTrue(self.version_a.validate_semantic_string(self.version_a.__str__()))
        # update version_a with non valid metadata
        self.version_a.metadata = 'non_valid@meta$strings'
        self.assertFalse(self.version_a.validate_semantic_string(self.version_a.__str__()))

        # test created object since they have already passed via validate_semantic_string function at init
        self.assertFalse(self.version_d.is_valid_semantic_version())
        self.assertEqual(self.version_d.invalid_version, '1.5.invalid')

        self.assertTrue(self.version_e.is_valid_semantic_version())
        self.assertEqual(self.version_e.version, [0, 0, 0])
        self.assertFalse(self.version_e.prefix)

        self.assertTrue(self.version_f.is_valid_semantic_version())
        self.assertEqual(self.version_f.version, [0, 0, 0])
        self.assertTrue(self.version_f.prefix)

        self.assertTrue(self.version_g.is_valid_semantic_version())
        self.assertEqual(self.version_g.version, [1, 0, 11111111111111111111111111111111111111111111111])
        self.assertTrue(self.version_g.prefix)

        self.assertTrue(self.version_h.is_valid_semantic_version())
        self.assertEqual(self.version_h.version, [13, 0, 75])
        self.assertFalse(self.version_h.prefix)

        self.assertTrue(self.version_j.is_valid_semantic_version())
        self.assertEqual(self.version_j.version, [3, 0, 1])
        self.assertTrue(self.version_j.prefix)
        self.assertEqual(self.version_j.release, 'alpha')

        self.assertTrue(self.version_l.is_valid_semantic_version())
        self.assertEqual(self.version_l.version, [0, 5, 0])
        self.assertFalse(self.version_l.prefix)
        self.assertEqual(self.version_l.release, 'alpha')
        self.assertEqual(self.version_l.metadata, 'meta-data.is-ok')

        self.assertFalse(self.version_n.is_valid_semantic_version())
        self.assertEqual(self.version_n.invalid_version, '      ')

        self.assertFalse(self.version_o.is_valid_semantic_version())
        self.assertEqual(self.version_o.invalid_version, '1.02.3')

        self.assertFalse(self.version_p.is_valid_semantic_version())
        self.assertEqual(self.version_p.invalid_version, '000.000.111')

        self.assertFalse(self.version_q.is_valid_semantic_version())
        self.assertEqual(self.version_q.invalid_version, '1.2.c')

        self.assertFalse(self.version_r.is_valid_semantic_version())
        self.assertEqual(self.version_r.invalid_version, 'V1.40.2')

        self.assertFalse(self.version_s.is_valid_semantic_version())
        self.assertEqual(self.version_s.invalid_version, 'v1.2.3.4')

        self.assertFalse(self.version_t.is_valid_semantic_version())
        self.assertEqual(self.version_t.invalid_version, '1.2.-3')

        self.assertFalse(self.version_u.is_valid_semantic_version())
        self.assertEqual(self.version_u.invalid_version, '1.9')

        self.assertFalse(self.version_v.is_valid_semantic_version())
        self.assertEqual(self.version_v.invalid_version, 'text')

        self.assertFalse(self.version_x.is_valid_semantic_version())
        self.assertEqual(self.version_x.invalid_version, 4)

        self.assertFalse(self.version_y.is_valid_semantic_version())
        self.assertEqual(self.version_y.invalid_version, True)

        self.assertFalse(self.version_z.is_valid_semantic_version())
        self.assertEqual(self.version_z.invalid_version, None)

    def test_pybump_version_string(self):
        self.assertEqual(str(self.version_a), '9.0.7-release-text+meta.text')
        self.assertEqual(str(self.version_c), '0.4.0+meta.text-with-some-num-123123')

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
        self.assertTrue(self.valid_version_1.is_valid_semantic_version())
        self.assertEqual(self.valid_version_1.version, [0, 12, 4])
        self.assertEqual(self.valid_version_1.prefix, False)
        self.assertEqual(self.valid_version_1.release, '')
        self.assertEqual(self.valid_version_1.metadata, '')

        self.assertTrue(self.valid_version_2.is_valid_semantic_version())
        self.assertEqual(self.valid_version_2.version, [1, 5, 0])
        self.assertEqual(self.valid_version_2.prefix, False)
        self.assertEqual(self.valid_version_2.release, 'alpha')
        self.assertEqual(self.valid_version_2.metadata, 'meta')

        self.assertFalse(self.invalid_version_1.is_valid_semantic_version())
        self.assertFalse(self.invalid_version_2.is_valid_semantic_version())
        self.assertEqual(self.invalid_version_2.invalid_version, '\n    version=1.5.0\n    ')

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
