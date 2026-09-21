import unittest
from os import access, chmod, makedirs, R_OK
from os.path import join
from shutil import rmtree
from subprocess import run, PIPE
from tempfile import mkdtemp


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


def simulate_set_version(file, version='', app_version=False, auto=False, metadata=False):
    """
    execute sub process to simulate real app execution,
    set new version to a file
    if auto is True, auto add git branch / hash
    if metadata is True (with auto), set SHA as metadata (+sha) instead of release (-sha)
    if app_version is True, then add the --app-version flag to execution
    :param file: string
    :param version: string
    :param app_version: boolean
    :param auto: boolean
    :param metadata: boolean
    :return: CompletedProcess object
    """
    if auto:
        cmd = ["python", "src/pybump.py", "set", "--file", file, "--auto"]
        if metadata:
            cmd.append("--metadata")
        if app_version:
            cmd.append("--app-version")
        return run(cmd, stdout=PIPE, stderr=PIPE)
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
        # simulate the 'set' command with --auto flag
        ################################################
        # first set test_valid_setup.py a simple version
        simulate_set_version("test/test_content_files/test_valid_setup.py", version="1.0.1")

        # test --auto sets release (-sha)
        test_set_auto = simulate_set_version("test/test_content_files/test_valid_setup.py", auto=True)
        self.assertRegex(test_set_auto.stdout.decode('utf-8').strip(),
                         r'\b1.0.1-[0-9a-f]{40}\b',
                         msg="test that 'test_set_auto' contains an hexadecimal string with exactly 40 characters")

        ########################################################
        # simulate the 'set' command with --auto --metadata flag
        ########################################################
        # reset to simple version
        simulate_set_version("test/test_content_files/test_valid_setup.py", version="2.0.0")

        # test --auto --metadata sets metadata (+sha) instead of release (-sha)
        test_set_auto_metadata = simulate_set_version("test/test_content_files/test_valid_setup.py",
                                                      auto=True, metadata=True)
        self.assertRegex(test_set_auto_metadata.stdout.decode('utf-8').strip(),
                         r'\b2.0.0\+[0-9a-f]{40}\b',
                         msg="test that '--auto --metadata' sets SHA as metadata (+sha), "
                             "output should match 2.0.0+<40-char-hex>")

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

    def test_yaml_sort_comments_preservation(self):
        """
        Test case that check YAML files are not sorted or missing original inline comments after version bumps
        :return:
        """
        # first "reset" version and appVersion with pre-defined values
        simulate_set_version("test/test_content_files/test_valid_chart.yaml", "1.0.0", app_version=False)
        simulate_set_version("test/test_content_files/test_valid_chart.yaml", "1.0.0", app_version=True)

        with open("test/test_content_files/test_valid_chart.yaml", "r") as f:
            content = f.read()

        # below text must be equal to the output of test_valid_chart.yaml file after bump action
        # this test will make sure all "# comments" preserved and key sorting did not occur
        self.assertMultiLineEqual(
            content,
            '# valid helm chart file\n'
            '# comments should stay here after YAML file handling\n'
            'apiVersion: v1\n'
            'appVersion: 1.0.0\n'
            'version: 1.0.0                    # version key should stay here and not be sorted\n'
            'description: A Helm chart for Kubernetes\n'
            'name: test\n'
            'plainText: |-\n'
            '  some data\n'
            '  here\n'
            'mapKey:\n'
            '  a: b\n'
            '\n'
            '  # above empty line will be preserved\n'
            '  bool: true\n'
            'listKey:\n'
            '- a\n'
            '- b\n'
            '- c\n')

    def test_package_version(self):
        """
        Test case when user is passing the version flag
        """
        # Verify valid string
        completed_process_object = run(["python", "src/pybump.py", "--version"],
                                       stdout=PIPE, stderr=PIPE)
        self.assertIs(completed_process_object.returncode, 0,
                      msg="tested 'version' flag that should always return exist 0, even on exceptions")

    def test_malformed_yaml_file(self):
        """
        Test that a YAML file which cannot be parsed exits cleanly with a clear
        message on stderr, rather than crashing with an UnboundLocalError traceback.
        See https://github.com/ArieLevs/PyBump/issues/63
        """
        malformed_file = "test/test_content_files/test_malformed_chart.yaml"

        # every sub command reads the file up front, so all three must fail the same way
        for completed_process_object in (
                simulate_get_version(malformed_file),
                simulate_bump_version(malformed_file, "patch"),
                simulate_set_version(malformed_file, "3.5.5")):
            stdout = completed_process_object.stdout.decode('utf-8')
            stderr = completed_process_object.stderr.decode('utf-8')

            self.assertEqual(completed_process_object.returncode, 1,
                             msg="malformed YAML file should exit with code 1")
            self.assertNotIn('Traceback', stderr,
                             msg="malformed YAML file should not crash with a traceback")
            self.assertIn(malformed_file, stderr,
                          msg="error message should name the file that failed to parse")
            self.assertEqual(stdout, '',
                             msg="parse errors belong on stderr, stdout should stay clean")


class PyBumpAutoFlagTest(unittest.TestCase):
    """
    Cover the '--auto' flag, which is the only consumer of GitPython in this project.
    The logic lives inline in main() which is marked '# pragma: no cover', so these
    run pybump as a sub process against throwaway repositories.
    See https://github.com/ArieLevs/PyBump/issues/71
    """

    def setUp(self):
        self.temp_dir = mkdtemp()
        self.addCleanup(rmtree, self.temp_dir, True)

    def init_repo(self, path, version='1.0.0'):
        """
        create a git repo containing a single committed setup.py, return its HEAD sha
        :param path: full path to the repo directory as string
        :param version: version string to write into setup.py
        :return: string, the 40 character commit sha
        """
        makedirs(path, exist_ok=True)
        self.git(path, 'init')
        with open(join(path, 'setup.py'), 'w') as setup_file:
            setup_file.write('setuptools.setup(\n    version="{0}",\n)\n'.format(version))

        self.git(path, 'add', '.')
        # disable signing, a developer machine with commit.gpgsign enabled would fail here
        self.git(path, '-c', 'user.email=test@pybump', '-c', 'user.name=test',
                 '-c', 'commit.gpgsign=false', 'commit', '-m', 'init')
        return self.git(path, 'rev-parse', 'HEAD').stdout.decode('utf-8').strip()

    @staticmethod
    def git(path, *args):
        """
        run a git command inside a given directory, raise if it fails
        :param path: full path to the repo directory as string
        :param args: git arguments
        :return: CompletedProcess object
        """
        completed_process_object = run(('git', '-C', path) + args, stdout=PIPE, stderr=PIPE)
        if completed_process_object.returncode != 0:
            raise RuntimeError('git {0} failed: {1}'.format(
                ' '.join(args), completed_process_object.stderr.decode('utf-8')))
        return completed_process_object

    def test_auto_sets_release_to_head_sha(self):
        repo_path = join(self.temp_dir, 'repo')
        head_sha = self.init_repo(repo_path)

        completed_process_object = simulate_set_version(join(repo_path, 'setup.py'), auto=True)
        self.assertEqual(completed_process_object.returncode, 0,
                         msg="'--auto' against a valid repo should exit 0")

        stdout = completed_process_object.stdout.decode('utf-8').strip()
        self.assertEqual(stdout, '1.0.0-{0}'.format(head_sha),
                         msg="'--auto' should set the real HEAD sha as release")

    def test_auto_metadata_sets_metadata_to_head_sha(self):
        repo_path = join(self.temp_dir, 'repo')
        head_sha = self.init_repo(repo_path, version='2.0.0')

        completed_process_object = simulate_set_version(join(repo_path, 'setup.py'), auto=True, metadata=True)
        self.assertEqual(completed_process_object.returncode, 0,
                         msg="'--auto --metadata' against a valid repo should exit 0")

        stdout = completed_process_object.stdout.decode('utf-8').strip()
        self.assertEqual(stdout, '2.0.0+{0}'.format(head_sha),
                         msg="'--auto --metadata' should set the real HEAD sha as metadata, not as release")

    def test_auto_on_detached_head(self):
        """
        on a detached HEAD 'repo.active_branch' raises TypeError, pybump should fall
        back to 'repo.head.object.hexsha' rather than propagate the exception
        """
        repo_path = join(self.temp_dir, 'repo')
        head_sha = self.init_repo(repo_path)
        self.git(repo_path, 'checkout', '--detach', 'HEAD')

        completed_process_object = simulate_set_version(join(repo_path, 'setup.py'), auto=True)
        self.assertEqual(completed_process_object.returncode, 0,
                         msg="'--auto' on a detached HEAD should exit 0 via the TypeError fallback")

        stdout = completed_process_object.stdout.decode('utf-8').strip()
        self.assertEqual(stdout, '1.0.0-{0}'.format(head_sha),
                         msg="detached HEAD should still resolve the same sha")

    def test_auto_from_sub_directory_finds_repo_root(self):
        """
        pybump passes 'search_parent_directories=True', a file nested below the repo
        root should still resolve to that repo
        """
        repo_path = join(self.temp_dir, 'repo')
        head_sha = self.init_repo(repo_path)

        nested_dir = join(repo_path, 'charts', 'nested')
        makedirs(nested_dir)
        with open(join(nested_dir, 'setup.py'), 'w') as setup_file:
            setup_file.write('setuptools.setup(\n    version="3.0.0",\n)\n')

        completed_process_object = simulate_set_version(join(nested_dir, 'setup.py'), auto=True)
        self.assertEqual(completed_process_object.returncode, 0,
                         msg="'--auto' on a file below the repo root should exit 0")

        stdout = completed_process_object.stdout.decode('utf-8').strip()
        self.assertEqual(stdout, '3.0.0-{0}'.format(head_sha),
                         msg="a nested file should resolve the sha of the repo above it")

    def test_auto_outside_a_git_repo(self):
        plain_dir = join(self.temp_dir, 'not_a_repo')
        makedirs(plain_dir)
        with open(join(plain_dir, 'setup.py'), 'w') as setup_file:
            setup_file.write('setuptools.setup(\n    version="1.0.0",\n)\n')

        completed_process_object = simulate_set_version(join(plain_dir, 'setup.py'), auto=True)
        self.assertEqual(completed_process_object.returncode, 1,
                         msg="'--auto' outside a git repo should exit 1")

        stderr = completed_process_object.stderr.decode('utf-8')
        self.assertIn('is not a valid git repo', stderr,
                      msg="should report that the directory is not a valid git repo")
        self.assertNotIn('Traceback', stderr,
                         msg="should fail cleanly, not raise InvalidGitRepositoryError")


class PyBumpErrorHandlingTest(unittest.TestCase):
    """
    Every user facing error should exit 1 with a message on stderr, never a traceback.
    See https://github.com/ArieLevs/PyBump/issues/74
    """

    def setUp(self):
        self.temp_dir = mkdtemp()
        self.addCleanup(rmtree, self.temp_dir, True)

    def write(self, name, content):
        """
        write a file into the test temp directory, return its full path
        :param name: file name as string
        :param content: file content as string
        :return: full path to the written file as string
        """
        path = join(self.temp_dir, name)
        with open(path, 'w') as target_file:
            target_file.write(content)
        return path

    def assert_clean_failure(self, completed_process_object, expected_text):
        """
        assert a run failed with exit 1 and a readable message rather than a traceback
        :param completed_process_object: CompletedProcess object
        :param expected_text: string expected to appear in stderr
        """
        stderr = completed_process_object.stderr.decode('utf-8')
        self.assertEqual(completed_process_object.returncode, 1,
                         msg="expected exit code 1, got {0}. stderr was: {1}".format(
                             completed_process_object.returncode, stderr))
        self.assertNotIn('Traceback', stderr,
                         msg="expected a clean message, got a traceback: {0}".format(stderr))
        self.assertIn(expected_text, stderr,
                      msg="stderr should mention '{0}', got: {1}".format(expected_text, stderr))

    def test_missing_file(self):
        self.assert_clean_failure(
            simulate_get_version(join(self.temp_dir, 'does_not_exist.yaml')), 'does_not_exist.yaml')

    def test_file_is_a_directory(self):
        directory_path = join(self.temp_dir, 'a_directory.yaml')
        makedirs(directory_path)
        self.assert_clean_failure(simulate_get_version(directory_path), 'a_directory.yaml')

    def test_unreadable_file(self):
        path = self.write('locked.yaml', 'apiVersion: v1\nname: t\nversion: 1.0.0\n')
        chmod(path, 0o000)
        self.addCleanup(chmod, path, 0o644)
        if access(path, R_OK):
            self.skipTest('running as a user that bypasses file permissions')

        self.assert_clean_failure(simulate_get_version(path), 'locked.yaml')

    def test_python_file_without_a_version(self):
        path = self.write('no_version.py', 'import setuptools\nsetuptools.setup(name="x")\n')
        self.assert_clean_failure(simulate_get_version(path), 'Unable to find version string')

    def test_python_file_with_multiple_versions(self):
        path = self.write('two_versions.py', 'version="1.0.0"\nversion="2.0.0"\n')
        self.assert_clean_failure(simulate_get_version(path), "More than one 'version' found")

    def test_yaml_that_is_not_a_helm_chart(self):
        path = self.write('not_a_chart.yaml', 'foo: bar\n')
        self.assert_clean_failure(simulate_get_version(path), 'not a valid Helm chart')

    def test_chart_without_app_version(self):
        path = self.write('no_app_version.yaml', 'apiVersion: v1\nname: t\nversion: 1.0.0\n')
        self.assert_clean_failure(simulate_get_version(path, app_version=True), "Could not find 'appVersion'")

    def test_unknown_file_extension(self):
        path = self.write('unknown.conf', 'version="1.0.0"\n')
        self.assert_clean_failure(simulate_get_version(path), 'not known to this app')


class PyBumpVersionFileTest(unittest.TestCase):
    """
    A VERSION file should keep whatever trailing newline it already had, and
    surrounding whitespace should not make it unreadable.
    See https://github.com/ArieLevs/PyBump/issues/76
    """

    def setUp(self):
        self.temp_dir = mkdtemp()
        self.addCleanup(rmtree, self.temp_dir, True)

    def write_version_file(self, content):
        """
        write a VERSION file into a fresh sub directory, return its full path
        :param content: exact bytes to write as string
        :return: full path to the VERSION file as string
        """
        directory = mkdtemp(dir=self.temp_dir)
        path = join(directory, 'VERSION')
        with open(path, 'w') as version_file:
            version_file.write(content)
        return path

    def read_raw(self, path):
        with open(path) as version_file:
            return version_file.read()

    def test_trailing_newline_is_preserved_on_bump(self):
        path = self.write_version_file('1.0.0\n')

        completed_process_object = simulate_bump_version(path, 'patch')
        self.assertEqual(completed_process_object.returncode, 0)
        self.assertEqual(self.read_raw(path), '1.0.1\n',
                         msg="a VERSION file that ended with a newline should keep it")

    def test_absent_trailing_newline_is_not_added_on_bump(self):
        path = self.write_version_file('1.0.0')

        completed_process_object = simulate_bump_version(path, 'patch')
        self.assertEqual(completed_process_object.returncode, 0)
        self.assertEqual(self.read_raw(path), '1.0.1',
                         msg="a VERSION file with no trailing newline should not gain one")

    def test_surrounding_whitespace_is_tolerated(self):
        path = self.write_version_file('1.2.3\n\n')

        completed_process_object = simulate_get_version(path)
        self.assertEqual(completed_process_object.returncode, 0,
                         msg="a blank line should not make the version unreadable")
        self.assertEqual(completed_process_object.stdout.decode('utf-8').strip(), '1.2.3')
