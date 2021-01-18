import unittest
from subprocess import run, PIPE


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
        return run(["python", "src/pybump.py", "get", "--file", file, "--app-version"], stdout=PIPE, stderr=PIPE)
    elif sem_ver:
        return run(["python", "src/pybump.py", "get", "--file", file, "--sem-ver"], stdout=PIPE, stderr=PIPE)
    elif release:
        return run(["python", "src/pybump.py", "get", "--file", file, "--release"], stdout=PIPE, stderr=PIPE)
    elif metadata:
        return run(["python", "src/pybump.py", "get", "--file", file, "--metadata"], stdout=PIPE, stderr=PIPE)
    else:
        return run(["python", "src/pybump.py", "get", "--file", file], stdout=PIPE, stderr=PIPE)


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
            return run(["python", "src/pybump.py", "set", "--file", file, "--auto", "--app-version"],
                       stdout=PIPE, stderr=PIPE)
        else:
            return run(["python", "src/pybump.py", "set", "--file", file, "--auto"],
                       stdout=PIPE, stderr=PIPE)
    else:
        if app_version:
            return run(["python", "src/pybump.py", "set", "--file", file, "--set-version", version, "--app-version"],
                       stdout=PIPE, stderr=PIPE)
        else:
            return run(["python", "src/pybump.py", "set", "--file", file, "--set-version", version],
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
        return run(["python", "src/pybump.py", "bump", "--level", level, "--file", file, "--app-version"],
                   stdout=PIPE, stderr=PIPE)
    else:
        return run(["python", "src/pybump.py", "bump", "--level", level, "--file", file],
                   stdout=PIPE, stderr=PIPE)


class PyBumpSimulatorTest(unittest.TestCase):

    def setUp(self):
        pass

    def test_bump_patch(self):
        #####################
        # simulate patch bump
        #####################
        simulate_set_version("test/test_content_files/test_valid_chart.yaml", "0.1.0")
        test_patch_1 = simulate_bump_version("test/test_content_files/test_valid_chart.yaml", "patch")
        self.assertEqual(test_patch_1.returncode, 0)

        test_patch_1 = simulate_get_version("test/test_content_files/test_valid_chart.yaml")
        self.assertEqual(test_patch_1.returncode, 0)

        stdout = test_patch_1.stdout.decode('utf-8').strip()
        self.assertEqual(stdout, '0.1.1', msg="return version should be 0.1.1")

        #############################################
        # simulate patch bump with --app-version flag
        #############################################
        simulate_set_version("test/test_content_files/test_valid_chart.yaml", "3.1.5", True)
        test_patch_2 = simulate_bump_version("test/test_content_files/test_valid_chart.yaml", "patch", True)
        self.assertEqual(test_patch_2.returncode, 0)

        test_patch_2 = simulate_get_version("test/test_content_files/test_valid_chart.yaml", True)
        self.assertEqual(test_patch_2.returncode, 0)

        stdout = test_patch_2.stdout.decode('utf-8').strip()
        self.assertEqual(stdout, '3.1.6', msg="return version should be 3.1.6")

        #################################
        # simulate patch bump with prefix
        #################################
        simulate_set_version("test/test_content_files/test_valid_chart.yaml", "v3.1.5")
        test_patch_3 = simulate_bump_version("test/test_content_files/test_valid_chart.yaml", "patch")
        self.assertEqual(test_patch_3.returncode, 0)

        test_patch_3 = simulate_get_version("test/test_content_files/test_valid_chart.yaml")
        self.assertEqual(test_patch_3.returncode, 0)

        stdout = test_patch_3.stdout.decode('utf-8').strip()
        self.assertEqual(stdout, 'v3.1.6', msg="return version should be v3.1.6")

    def test_bump_minor(self):
        #####################
        # simulate minor bump
        #####################
        simulate_set_version("test/test_content_files/test_valid_setup.py", "2.1.5-alpha+metadata.is.useful")
        test_minor_1 = simulate_bump_version("test/test_content_files/test_valid_setup.py", "minor")
        self.assertEqual(test_minor_1.returncode, 0)

        test_minor_1 = simulate_get_version("test/test_content_files/test_valid_setup.py")
        self.assertEqual(test_minor_1.returncode, 0)

        stdout = test_minor_1.stdout.decode('utf-8').strip()
        self.assertEqual(stdout, '2.2.0-alpha+metadata.is.useful',
                         msg="return version should be 2.2.0-alpha+metadata.is.useful")

    def test_bump_major(self):
        #####################
        # simulate major bump
        #####################
        simulate_set_version("test/test_content_files/test_valid_chart.yaml", "0.5.9")
        test_major_1 = simulate_bump_version("test/test_content_files/test_valid_chart.yaml", "major")
        self.assertEqual(test_major_1.returncode, 0)

        test_major_1 = simulate_get_version("test/test_content_files/test_valid_chart.yaml")
        self.assertEqual(test_major_1.returncode, 0)

        stdout = test_major_1.stdout.decode('utf-8').strip()
        self.assertEqual(stdout, '1.0.0', msg="return version should be 1.0.0")

        #############################################
        # simulate major bump with --app-version flag
        #############################################
        simulate_set_version("test/test_content_files/test_valid_chart.yaml", "2.2.8", True)
        test_major_2 = simulate_bump_version("test/test_content_files/test_valid_chart.yaml", "major", True)
        self.assertEqual(test_major_2.returncode, 0)

        test_major_2 = simulate_get_version("test/test_content_files/test_valid_chart.yaml", True)
        self.assertEqual(test_major_2.returncode, 0)

        stdout = test_major_2.stdout.decode('utf-8').strip()
        self.assertEqual(stdout, '3.0.0', msg="return version should be 3.0.0")

        ######################################################################################
        # simulate major bump with --app-version flag on a chart with missing appVersion field
        ######################################################################################
        test_major_3 = simulate_bump_version("test/test_content_files/test_valid_chart_minimal.yaml", "major", True)
        self.assertEqual(test_major_3.returncode, 1,
                         msg="returned 0 exist code, but tested bump against a chart file with missing appVersion key")

    def test_invalid_bump_major(self):
        simulate_set_version("test/test_content_files/test_invalid_chart.yaml", "3.5.5")
        completed_process_object = simulate_bump_version("test/test_content_files/test_invalid_chart.yaml", "major")
        self.assertNotEqual(completed_process_object.returncode, 0,
                            msg="returned a 0 exist code, but tested bump version against a non valid chart file")

    def test_invalid_set_version(self):
        completed_process_object = simulate_set_version("test/test_content_files/test_valid_setup.py", "V3.2.0")
        self.assertNotEqual(completed_process_object.returncode, 0,
                            msg="returned a 0 exist code, but tested set version against a non valid semver")

    def test_get_flags(self):
        simulate_set_version("test/test_content_files/test_valid_chart.yaml", "2.0.8-alpha.802+sha-256")

        ##################################################
        # simulate the 'get' command with '--sem-ver' flag
        ##################################################
        test_get_sem_ver = simulate_get_version("test/test_content_files/test_valid_chart.yaml", sem_ver=True)
        self.assertEqual(test_get_sem_ver.returncode, 0,
                         msg="returned a non 0 exist code, but tested get version against a valid chart file")

        stdout = test_get_sem_ver.stdout.decode('utf-8').strip()
        self.assertEqual(stdout, '2.0.8',
                         msg="return sem-ver version should be 2.0.8")

        ##################################################
        # simulate the 'get' command with '--release' flag
        ##################################################
        test_get_release = simulate_get_version("test/test_content_files/test_valid_chart.yaml", release=True)
        self.assertEqual(test_get_release.returncode, 0,
                         msg="returned a non 0 exist code, but tested get version against a valid chart file")

        stdout = test_get_release.stdout.decode('utf-8').strip()
        self.assertEqual(stdout, 'alpha.802',
                         msg="return release string should be alpha.802")

        ###################################################
        # simulate the 'get' command with '--metadata' flag
        ###################################################
        test_get_metadata = simulate_get_version("test/test_content_files/test_valid_chart.yaml", metadata=True)
        self.assertEqual(test_get_metadata.returncode, 0,
                         msg="returned a non 0 exist code, but tested get version against a valid chart file")

        stdout = test_get_metadata.stdout.decode('utf-8').strip()
        self.assertEqual(stdout, 'sha-256',
                         msg="return metadata string should be sha-256")

        ################################################
        # simulate the 'get' command with version prefix
        ################################################
        simulate_set_version("test/test_content_files/test_valid_chart.yaml", "v2.0.8-alpha.802+sha-256")
        test_get_prefix = simulate_get_version("test/test_content_files/test_valid_chart.yaml")
        self.assertEqual(test_get_prefix.returncode, 0,
                         msg="returned a non 0 exist code, but tested get version against a valid chart file")

        stdout = test_get_prefix.stdout.decode('utf-8').strip()
        self.assertEqual(stdout, 'v2.0.8-alpha.802+sha-256',
                         msg="return string should be v2.0.8-alpha.802+sha-256")
        if stdout != "v2.0.8-alpha.802+sha-256":
            raise Exception("test_get_flags failed, return string should be v2.0.8-alpha.802+sha-256 got " + stdout)

        #############################################################################################
        # simulate the 'get' command with --app-version flag on a chart with missing appVersion field
        #############################################################################################
        test_get_missing_app_version = simulate_get_version(
            "test/test_content_files/test_valid_chart_minimal.yaml", app_version=True
        )
        self.assertEqual(test_get_missing_app_version.returncode, 1,
                         msg="returned a 0 exist code, "
                             "but tested get 'app-version' flag against a chart file with missing appVersion key")

    def test_set_flags(self):
        ################################################
        # simulate the 'set' command with version prefix
        ################################################
        # this path test/test_content_files/ is not a valid git repo (its parent is),
        # so it should fail with relevant error
        test_set_auto = simulate_set_version("test/test_content_files/test_valid_setup.py", auto=True)
        self.assertEqual('test/test_content_files is not a valid git repo',
                         test_set_auto.stderr.decode('utf-8').strip())

        # Currently not testing success with auto flag since git branch / hash is dynamic

        # test invalid version set
        test_set_auto = simulate_set_version("test/test_content_files/test_valid_setup.py", version='V123.x.4')
        self.assertEqual('Invalid semantic version format: V123.x.4\nMake sure to comply with https://semver.org/ '
                         '(lower case \'v\' prefix is allowed)',
                         test_set_auto.stderr.decode('utf-8').strip())

    def test_plain_text_version_file(self):
        """
        Test case when target file is a 'VERSION' file
        """
        completed_process_object = simulate_get_version("test/test_content_files/VERSION")
        self.assertEqual(completed_process_object.returncode, 0,
                         msg="returned a non 0 exist code, but tested get version against a valid VERSION file")

        stdout = completed_process_object.stdout.decode('utf-8').strip()
        self.assertEqual(stdout, '2.5.1+metadata.here', msg="return version should be 2.5.1+metadata.here")

        simulate_bump_version("test/test_content_files/VERSION", "major")
        completed_process_object = simulate_get_version("test/test_content_files/VERSION")
        self.assertEqual(completed_process_object.returncode, 0,
                         msg="returned a non 0 exist code, but tested bump version against a valid VERSION file")

        stdout = completed_process_object.stdout.decode('utf-8').strip()
        self.assertEqual(stdout, '3.0.0+metadata.here')

    def test_verify_flag(self):
        """
        Test case when user is verifying string
        """
        # Verify valid string
        completed_process_object = run(["python", "src/pybump.py", "--verify", "123.45.6789+valid-version"],
                                       stdout=PIPE, stderr=PIPE)
        self.assertIs(completed_process_object.returncode, 0,
                      msg="returned a non 0 exist code, but tested 'verify' flag against a valid semver string")

        # Verify invalid string
        completed_process_object = run(["python", "src/pybump.py", "--verify", "1.1-my-feature"],
                                       stdout=PIPE, stderr=PIPE)
        self.assertIs(completed_process_object.returncode, 1,
                      msg="returned a 0 exist code, but tested 'verify' flag against a non valid semver string")
