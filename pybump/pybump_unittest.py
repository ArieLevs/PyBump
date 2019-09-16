import unittest
from subprocess import run, PIPE

from pybump.pybump import *

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
valid_version_file_2 = """

    1.5.0
    
    
    """
invalid_version_file_1 = """
    this is some text in addition to version
    1.5.0
    nothing except semantic version should be in this file 
    """
invalid_version_file_2 = """
    version=1.5.0
    """


def get_version(file):
    return run(["python", "pybump/pybump.py", "get", "--file", file],
               stdout=PIPE, stderr=PIPE)

def get_appversion(file):
    return run(["python", "pybump/pybump.py", "get", "--appversion", "--file", file],
               stdout=PIPE, stderr=PIPE)


def set_version(file, version):
    return run(["python", "pybump/pybump.py", "set", "--file", file, "--set-version", version],
               stdout=PIPE, stderr=PIPE)


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

    def test_is_valid_version_file(self):
        self.assertTrue(is_semantic_string(valid_version_file_1))
        self.assertTrue(is_semantic_string(valid_version_file_2))
        self.assertFalse(is_semantic_string(invalid_version_file_1))
        self.assertFalse(is_semantic_string(invalid_version_file_2))
        self.assertEqual(is_semantic_string(valid_version_file_1), [0, 12, 4])

    @staticmethod
    def test_bump_patch():
        set_version("pybump/test_valid_chart.yaml", "0.1.0")
        completed_process_object = run(["python", "pybump/pybump.py", "bump",
                                        "--level", "patch",
                                        "--file", "pybump/test_valid_chart.yaml"],
                                       stdout=PIPE,
                                       stderr=PIPE)

        if completed_process_object.returncode != 0:
            raise Exception(completed_process_object.stderr.decode('utf-8'))

        completed_process_object = get_version("pybump/test_valid_chart.yaml")
        if completed_process_object.returncode != 0:
            raise Exception(completed_process_object.stderr.decode('utf-8'))

        stdout = completed_process_object.stdout.decode('utf-8').strip()
        if stdout != "0.1.1":
            raise Exception("test_bump_patch failed, return version should be 0.1.1 got " + stdout)

    @staticmethod
    def test_bump_minor():
        set_version("pybump/test_valid_setup.py", "2.1.5")
        completed_process_object = run(["python", "pybump/pybump.py", "bump",
                                        "--level", "minor",
                                        "--file", "pybump/test_valid_setup.py"],
                                       stdout=PIPE,
                                       stderr=PIPE)

        if completed_process_object.returncode != 0:
            raise Exception(completed_process_object.stderr.decode('utf-8'))

        completed_process_object = get_version("pybump/test_valid_setup.py")
        if completed_process_object.returncode != 0:
            raise Exception(completed_process_object.stderr.decode('utf-8'))

        stdout = completed_process_object.stdout.decode('utf-8').strip()
        if stdout != "2.2.0":
            raise Exception("test_bump_minor failed, return version should be 2.2.0 got " + stdout)

    @staticmethod
    def test_bump_major():
        set_version("pybump/test_valid_chart.yaml", "0.5.9")
        completed_process_object = run(["python", "pybump/pybump.py", "bump",
                                        "--level", "major",
                                        "--file", "pybump/test_valid_chart.yaml"],
                                       stdout=PIPE,
                                       stderr=PIPE)

        if completed_process_object.returncode != 0:
            raise Exception(completed_process_object.stderr.decode('utf-8'))

        completed_process_object = get_version("pybump/test_valid_chart.yaml")
        if completed_process_object.returncode != 0:
            raise Exception(completed_process_object.stderr.decode('utf-8'))

        stdout = completed_process_object.stdout.decode('utf-8').strip()
        if stdout != "1.0.0":
            raise Exception("test_bump_major failed, return version should be 1.0.0 got " + stdout)

    @staticmethod
    def test_invalid_bump_major():
        set_version("pybump/test_invalid_chart.yaml", "3.5.5")
        completed_process_object = run(["python", "pybump/pybump.py", "bump",
                                        "--level", "major",
                                        "--file", "pybump/test_invalid_chart.yaml"],
                                       stdout=PIPE,
                                       stderr=PIPE)
        if completed_process_object.returncode != 0:
            pass
        else:
            raise Exception("test_invalid_bump_major failed, test should of fail, but passed")

    @staticmethod
    def test_get_appversion():
        completed_process_object = get_appversion("pybump/test_valid_chart.yaml")
        if completed_process_object.returncode != 0:
            raise Exception(completed_process_object.stderr.decode('utf-8'))
        stdout = completed_process_object.stdout.decode('utf-8').strip()
        if stdout != "1.0":
            raise Exception("test_get_appversion failed, return version should be 1.0 got " + stdout)

if __name__ == '__main__':
    unittest.main()
