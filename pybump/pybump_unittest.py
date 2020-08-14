import unittest
from subprocess import run, PIPE

from pybump.pybump import get_setup_py_version, set_setup_py_version, \
    is_semantic_string, bump_version, is_valid_helm_chart, assemble_version_string, \
    write_version_to_file, read_version_from_file

valid_helm_chart = {'apiVersion': 'v1',
                    'appVersion': '1.0',
                    'description': 'A Helm chart for Kubernetes',
                    'name': 'test',
                    'version': '0.1.0'}
invalid_helm_chart = {'apiVersion': 'v1',
                      'notAppVersionKeyHere': '1.0',
                      'description': 'A Helm chart for Kubernetes',
                      'version': '0.1.0'}
empty_helm_chart = {}

valid_setup_py = """
    setuptools.setup(
        name="pybump",
        version="0.1.3",
        author="Arie Lev",
        author_email="levinsonarie@gmail.com",
        description="Python version bumper",
        long_description=long_description,
        long_description_content_type="text/markdown",
        url="https://github.com/ArieLevs/PyBump",
        license='Apache License 2.0',
        packages=setuptools.find_packages(),
    )
    """

# This setup.py content is missing 'version' key
invalid_setup_py_1 = """
    setuptools.setup(
        name="pybump",
        invalid_version_string="0.1.3",
        author="Arie Lev",
        author_email="levinsonarie@gmail.com",
        description="Python version bumper",
    )
    """
# This setup.py content 'version' key declared 3 times
invalid_setup_py_2 = """
    setuptools.setup(
        name="pybump",
        version="0.1.3",
        version="0.1.2",
        __version__="12356"
        author="Arie Lev",
        author_email="levinsonarie@gmail.com",
        description="Python version bumper",
    )
    """

valid_version_file_1 = """0.12.4"""
valid_version_file_2 = """1.5.0-alpha+meta"""
invalid_version_file_1 = """
    this is some text in addition to version
    1.5.0
    nothing except semantic version should be in this file
    """
invalid_version_file_2 = """
    version=1.5.0
    """


def simulate_get_version(file, app_version=False, sem_ver=False, release=False, metadata=False):
    """
    execute sub process to simulate real app execution,
    return current version from a file
    if app_version is True, then add the --app-version flag to execution
    :param file: string
    :param app_version: boolean
    :param sem_ver: boolean
    :param release: boolean
    :param metadata: boolean
    :return: CompletedProcess object
    """
    if app_version:
        return run(["python", "pybump/pybump.py", "get", "--file", file, "--app-version"], stdout=PIPE, stderr=PIPE)
    elif sem_ver:
        return run(["python", "pybump/pybump.py", "get", "--file", file, "--sem-ver"], stdout=PIPE, stderr=PIPE)
    elif release:
        return run(["python", "pybump/pybump.py", "get", "--file", file, "--release"], stdout=PIPE, stderr=PIPE)
    elif metadata:
        return run(["python", "pybump/pybump.py", "get", "--file", file, "--metadata"], stdout=PIPE, stderr=PIPE)
    else:
        return run(["python", "pybump/pybump.py", "get", "--file", file], stdout=PIPE, stderr=PIPE)


def simulate_set_version(file, version='', app_version=False, auto=False):
    """
    execute sub process to simulate real app execution,
    set new version to a file
    if auto is True, auto add git branch / hash
    if app_version is True, then add the --app-version flag to execution
    :param file: string
    :param version: string
    :param app_version: boolean
    :param auto: boolean
    :return: CompletedProcess object
    """
    if auto:
        if app_version:
            return run(["python", "pybump/pybump.py", "set", "--file", file, "--auto", "--app-version"],
                       stdout=PIPE, stderr=PIPE)
        else:
            return run(["python", "pybump/pybump.py", "set", "--file", file, "--auto"],
                       stdout=PIPE, stderr=PIPE)
    else:
        if app_version:
            return run(["python", "pybump/pybump.py", "set", "--file", file, "--set-version", version, "--app-version"],
                       stdout=PIPE, stderr=PIPE)
        else:
            return run(["python", "pybump/pybump.py", "set", "--file", file, "--set-version", version],
                       stdout=PIPE, stderr=PIPE)


def simulate_bump_version(file, level, app_version=False):
    """
    execute sub process to simulate real app execution,
    bump version in file based on level
    if app_version is True, then add the --app-version flag to execution
    :param file: string
    :param level: string
    :param app_version: boolean
    :return:
    """
    if app_version:
        return run(["python", "pybump/pybump.py", "bump", "--level", level, "--file", file, "--app-version"],
                   stdout=PIPE, stderr=PIPE)
    else:
        return run(["python", "pybump/pybump.py", "bump", "--level", level, "--file", file],
                   stdout=PIPE, stderr=PIPE)


class PyBumpTest(unittest.TestCase):

    def setUp(self):
        pass

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

    def test_bump_version(self):
        self.assertEqual(bump_version([9, 0, 7], 'major'), [10, 0, 0])
        self.assertEqual(bump_version([1, 2, 3], 'major'), [2, 0, 0])
        self.assertEqual(bump_version([1, 2, 3], 'minor'), [1, 3, 0])
        self.assertEqual(bump_version([1, 2, 3], 'patch'), [1, 2, 4])
        self.assertEqual(bump_version([0, 0, 9], 'patch'), [0, 0, 10])

        self.assertRaises(ValueError, bump_version, None, 'patch')
        self.assertRaises(ValueError, bump_version, [1, 2, 3], 'not_patch')

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

    def test_assemble_version_string(self):
        self.assertEqual(
            assemble_version_string(prefix=True, version_array=[1, 4, 0], release='release_text', metadata='meta_text'),
            'v1.4.0-release_text+meta_text')
        self.assertEqual(
            assemble_version_string(prefix=False, version_array=[1, 4, 0], release='', metadata='meta_text'),
            '1.4.0+meta_text')
        self.assertEqual(
            assemble_version_string(prefix=False, version_array=[0, 4, 0], release='', metadata=''),
            '0.4.0')

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
             'version': '1.1.2'}
        )

        self.assertEqual(read_version_from_file(
            file_path='test_write_read_file_2.yaml', app_version=True),
            {'file_content': {'apiVersion': 'v1',
                              'appVersion': '1.1.2',
                              'name': 'test',
                              'version': '0.1.0'},
             'version': '1.1.2'}
        )

        self.assertEqual(read_version_from_file(
            file_path='test_write_read_file.py', app_version=False),
            {'file_content': 'some text before version="1.1.2", and some text after',
             'version': '1.1.2'}
        )

        self.assertEqual(read_version_from_file(
            file_path='VERSION', app_version=False),
            {'file_content': None,
             'version': '1.1.2'}
        )

    @staticmethod
    def test_bump_patch():
        #####################
        # simulate patch bump
        #####################
        simulate_set_version("pybump/test_content_files/test_valid_chart.yaml", "0.1.0")
        test_patch_1 = simulate_bump_version("pybump/test_content_files/test_valid_chart.yaml", "patch")

        if test_patch_1.returncode != 0:
            raise Exception(test_patch_1.stderr.decode('utf-8'))

        test_patch_1 = simulate_get_version("pybump/test_content_files/test_valid_chart.yaml")
        if test_patch_1.returncode != 0:
            raise Exception(test_patch_1.stderr.decode('utf-8'))

        stdout = test_patch_1.stdout.decode('utf-8').strip()
        if stdout != "0.1.1":
            raise Exception("test_bump_patch failed, return version should be 0.1.1 got " + stdout)

        #############################################
        # simulate patch bump with --app-version flag
        #############################################
        simulate_set_version("pybump/test_content_files/test_valid_chart.yaml", "3.1.5", True)
        test_patch_2 = simulate_bump_version("pybump/test_content_files/test_valid_chart.yaml", "patch", True)

        if test_patch_2.returncode != 0:
            raise Exception(test_patch_2.stderr.decode('utf-8'))

        test_patch_2 = simulate_get_version("pybump/test_content_files/test_valid_chart.yaml", True)
        if test_patch_2.returncode != 0:
            raise Exception(test_patch_2.stderr.decode('utf-8'))

        stdout = test_patch_2.stdout.decode('utf-8').strip()
        if stdout != "3.1.6":
            raise Exception("test_bump_patch failed, return version should be 3.1.6 got " + stdout)

        #################################
        # simulate patch bump with prefix
        #################################
        simulate_set_version("pybump/test_content_files/test_valid_chart.yaml", "v3.1.5")
        test_patch_3 = simulate_bump_version("pybump/test_content_files/test_valid_chart.yaml", "patch")

        if test_patch_3.returncode != 0:
            raise Exception(test_patch_3.stderr.decode('utf-8'))

        test_patch_3 = simulate_get_version("pybump/test_content_files/test_valid_chart.yaml")
        if test_patch_3.returncode != 0:
            raise Exception(test_patch_3.stderr.decode('utf-8'))

        stdout = test_patch_3.stdout.decode('utf-8').strip()
        if stdout != "v3.1.6":
            raise Exception("test_bump_patch failed, return version should be v3.1.6 got " + stdout)

    @staticmethod
    def test_bump_minor():
        #####################
        # simulate minor bump
        #####################
        simulate_set_version("pybump/test_content_files/test_valid_setup.py", "2.1.5-alpha+metadata.is.useful")
        test_minor_1 = simulate_bump_version("pybump/test_content_files/test_valid_setup.py", "minor")

        if test_minor_1.returncode != 0:
            raise Exception(test_minor_1.stderr.decode('utf-8'))

        test_minor_1 = simulate_get_version("pybump/test_content_files/test_valid_setup.py")
        if test_minor_1.returncode != 0:
            raise Exception(test_minor_1.stderr.decode('utf-8'))

        stdout = test_minor_1.stdout.decode('utf-8').strip()
        if stdout != "2.2.0-alpha+metadata.is.useful":
            raise Exception("test_bump_minor failed, "
                            "return version should be 2.2.0-alpha+metadata.is.useful got " + stdout)

    @staticmethod
    def test_bump_major():
        #####################
        # simulate major bump
        #####################
        simulate_set_version("pybump/test_content_files/test_valid_chart.yaml", "0.5.9")
        test_major_1 = simulate_bump_version("pybump/test_content_files/test_valid_chart.yaml", "major")
        if test_major_1.returncode != 0:
            raise Exception(test_major_1.stderr.decode('utf-8'))

        test_major_1 = simulate_get_version("pybump/test_content_files/test_valid_chart.yaml")
        if test_major_1.returncode != 0:
            raise Exception(test_major_1.stderr.decode('utf-8'))

        stdout = test_major_1.stdout.decode('utf-8').strip()
        if stdout != "1.0.0":
            raise Exception("test_bump_major failed, return version should be 1.0.0 got " + stdout)

        #############################################
        # simulate major bump with --app-version flag
        #############################################
        simulate_set_version("pybump/test_valid_chart.yaml", "2.2.8", True)
        test_major_2 = simulate_bump_version("pybump/test_content_files/test_valid_chart.yaml", "major", True)

        if test_major_2.returncode != 0:
            raise Exception(test_major_2.stderr.decode('utf-8'))

        test_major_2 = simulate_get_version("pybump/test_content_files/test_valid_chart.yaml", True)
        if test_major_2.returncode != 0:
            raise Exception(test_major_2.stderr.decode('utf-8'))

        stdout = test_major_2.stdout.decode('utf-8').strip()
        if stdout != "3.0.0":
            raise Exception("test_bump_patch failed, return version should be 3.0.0 got " + stdout)

        ######################################################################################
        # simulate major bump with --app-version flag on a chart with missing appVersion field
        ######################################################################################
        test_major_3 = simulate_bump_version("pybump/test_content_files/test_valid_chart_minimal.yaml", "major", True)

        if test_major_3.returncode == 1:
            # 'CompletedProcess' should raised exception
            pass
        else:
            raise Exception("test_bump_major with missing appVersion failed, "
                            "test should of fail with ValueError, but it passed passed")

    @staticmethod
    def test_invalid_bump_major():
        simulate_set_version("pybump/test_content_files/test_invalid_chart.yaml", "3.5.5")
        completed_process_object = simulate_bump_version("pybump/test_content_files/test_invalid_chart.yaml", "major")
        if completed_process_object.returncode != 0:
            pass
        else:
            raise Exception("test_invalid_bump_major failed, test should of fail, but passed")

    @staticmethod
    def test_invalid_set_version():
        completed_process_object = simulate_set_version("pybump/test_content_files/test_valid_setup.py", "V3.2.0")
        if completed_process_object.returncode != 0:
            pass
        else:
            raise Exception("test_invalid_set_version failed (invalid version), test should of fail, but passed")

    @staticmethod
    def test_get_flags():
        simulate_set_version("pybump/test_content_files/test_valid_chart.yaml", "2.0.8-alpha.802+sha-256")

        ##################################################
        # simulate the 'get' command with '--sem-ver' flag
        ##################################################
        test_get_sem_ver = simulate_get_version("pybump/test_content_files/test_valid_chart.yaml", sem_ver=True)
        if test_get_sem_ver.returncode != 0:
            raise Exception(test_get_sem_ver.stderr.decode('utf-8'))

        stdout = test_get_sem_ver.stdout.decode('utf-8').strip()
        if stdout != "2.0.8":
            raise Exception("test_get_flags failed, return sem-ver version should be 2.0.8 got " + stdout)

        ##################################################
        # simulate the 'get' command with '--release' flag
        ##################################################
        test_get_release = simulate_get_version("pybump/test_content_files/test_valid_chart.yaml", release=True)
        if test_get_release.returncode != 0:
            raise Exception(test_get_release.stderr.decode('utf-8'))

        stdout = test_get_release.stdout.decode('utf-8').strip()
        if stdout != "alpha.802":
            raise Exception("test_get_flags failed, return release string should be alpha.802 got " + stdout)

        ###################################################
        # simulate the 'get' command with '--metadata' flag
        ###################################################
        test_get_metadata = simulate_get_version("pybump/test_content_files/test_valid_chart.yaml", metadata=True)
        if test_get_metadata.returncode != 0:
            raise Exception(test_get_metadata.stderr.decode('utf-8'))

        stdout = test_get_metadata.stdout.decode('utf-8').strip()
        if stdout != "sha-256":
            raise Exception("test_get_flags failed, return metadata string should be sha-256 got " + stdout)

        ################################################
        # simulate the 'get' command with version prefix
        ################################################
        simulate_set_version("pybump/test_content_files/test_valid_chart.yaml", "v2.0.8-alpha.802+sha-256")
        test_get_prefix = simulate_get_version("pybump/test_content_files/test_valid_chart.yaml")
        if test_get_prefix.returncode != 0:
            raise Exception(test_get_prefix.stderr.decode('utf-8'))

        stdout = test_get_prefix.stdout.decode('utf-8').strip()
        if stdout != "v2.0.8-alpha.802+sha-256":
            raise Exception("test_get_flags failed, return string should be v2.0.8-alpha.802+sha-256 got " + stdout)

        #############################################################################################
        # simulate the 'get' command with --app-version flag on a chart with missing appVersion field
        #############################################################################################
        test_get_missing_app_version = simulate_get_version(
            "pybump/test_content_files/test_valid_chart_minimal.yaml", app_version=True
        )
        if test_get_missing_app_version.returncode == 1:
            # 'CompletedProcess' should raised exception
            pass
        else:
            raise Exception("test_get_flags with missing appVersion failed, "
                            "test should of fail with ValueError, but it passed passed")

    def test_set_flags(self):
        ################################################
        # simulate the 'get' command with version prefix
        ################################################
        # this path pybump/test_content_files/ is not a valid git repo (its parent is),
        # so it should fail with relevant error
        test_set_auto = simulate_set_version("pybump/test_content_files/test_valid_setup.py", auto=True)
        self.assertEqual('pybump/test_content_files is not a valid git repo',
                         test_set_auto.stderr.decode('utf-8').strip())

        # Currently not testing success with auto flag since git branch / hash is dynamic

    @staticmethod
    def test_plain_text_version_file():
        """
        Test case when target file is a 'VERSION' file
        """
        completed_process_object = simulate_get_version("pybump/test_content_files/VERSION")
        if completed_process_object.returncode != 0:
            raise Exception(completed_process_object.stderr.decode('utf-8'))
        stdout = completed_process_object.stdout.decode('utf-8').strip()
        if stdout != "2.5.1+metadata.here":
            raise Exception("test_plain_text_version_file failed, "
                            "return version should be 2.5.1+metadata.here got " + stdout)

        simulate_bump_version("pybump/test_content_files/VERSION", "major")
        completed_process_object = simulate_get_version("pybump/test_content_files/VERSION")
        if completed_process_object.returncode != 0:
            raise Exception(completed_process_object.stderr.decode('utf-8'))

        stdout = completed_process_object.stdout.decode('utf-8').strip()
        if stdout != "3.0.0+metadata.here":
            raise Exception("test_plain_text_version_file failed, "
                            "return version should be 3.0.0+metadata.here got " + stdout)

    @staticmethod
    def test_verify_flag():
        """
        Test case when user is verifying string
        """
        # Verify valid string
        completed_process_object = run(["python", "pybump/pybump.py", "--verify", "123.45.6789+valid-version"],
                                       stdout=PIPE, stderr=PIPE)
        if completed_process_object.returncode != 0:
            raise Exception(completed_process_object.stderr.decode('utf-8'))

        # Verify invalid string
        completed_process_object = run(["python", "pybump/pybump.py", "--verify", "1.1-my-feature"],
                                       stdout=PIPE, stderr=PIPE)
        if completed_process_object.returncode == 1:
            pass
        else:
            raise Exception("test_verify_flag invalid string failed, test should of fail, but passed")


if __name__ == '__main__':
    unittest.main()
