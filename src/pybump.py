import argparse
import os
import re
from sys import stderr

import yaml
from pkg_resources import get_distribution, DistributionNotFound

regex_version_pattern = re.compile(r"((?:__)?version(?:__)? ?= ?[\"'])(.+?)([\"'])")


class PybumpVersion(object):

    def __init__(self, version):
        self.__prefix = False
        self.__version = [0, 0, 0]
        self.__release = None
        self.__metadata = None
        self.__valid_sem_ver = False
        self.__invalid_version = None
        self.validate_semantic_string(version)

    def validate_semantic_string(self, version):
        """
        init the PybumpVersion object by getting a plain text version string,
        init will check if input string is a semantic version
        semver defined here: https://github.com/semver/semver/blob/master/semver.md,
        The version is allowed a lower case 'v' character.
        search a match according to the regular expresion, so for example '1.1.2-prerelease+meta' is valid,
        then make sure there is and exact single match and validate if each of x,y,z is an integer.

        in case a non valid version passed, 'valid_sem_ver' will stay False

        :param version: string
        """
        orig_version = version
        # only if passed version is non empty string
        if type(version) == str and len(version) != 0:
            # In case the version if of type 'v2.2.5' then save 'v' prefix and cut it for further 'semver' validation
            if version[0] == 'v':
                version = version[1:]
                self.__prefix = True

            semver_regex = re.compile(r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)"  # Match x.y.z
                                      # Match -sometext-12.here
                                      r"(?:-((?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*)"
                                      r"(?:\.(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*))*))?"
                                      # Match +more.123.here
                                      r"(?:\+([0-9a-zA-Z-]+(?:\.[0-9a-zA-Z-]+)*))?$")
            # returns a list of tuples, for example [('2', '2', '7', 'alpha', '')]
            match = semver_regex.findall(version)

            # if there was no match using 'semver_regex', then empty list returned
            if len(match) != 0:
                try:
                    self.__version = [int(n) for n in match[0][:3]]

                    self.__release = match[0][3]
                    self.__metadata = match[0][4]

                    self.__valid_sem_ver = True
                    self.__invalid_version = None
                    return True
                except ValueError:
                    pass
        self.__valid_sem_ver = False
        self.__invalid_version = orig_version
        return False

    @property
    def version(self):
        return self.__version

    @property
    def prefix(self):
        return self.__prefix

    @property
    def release(self):
        return self.__release

    @release.setter
    def release(self, value):
        self.__release = value
        # re validate that updated version with new release is still valid
        self.validate_semantic_string(self.__str__())

    @property
    def metadata(self):
        return self.__metadata

    @metadata.setter
    def metadata(self, value):
        # re validate that updated version with new metadata is still valid
        self.__metadata = value
        self.validate_semantic_string(self.__str__())

    @property
    def invalid_version(self):
        return self.__invalid_version

    def __str__(self):
        """
        reconstruct version to string, if releases or metadata passed, override the one that is part of object
        :return: string
        """
        result_string = ''
        if self.prefix:
            result_string = 'v'
        result_string += '.'.join(str(x) for x in self.__version)

        if self.release:
            result_string += '-' + self.release

        if self.metadata:
            result_string += '+' + self.metadata

        return result_string

    def bump_version(self, level):
        """
        Perform ++1 action on the array [x, y, z] cell,
        :param level: string represents major|minor|patch
        :return: int array with new value
        """
        if level == 'major':
            self.__version[0] += 1
            self.__version[1] = 0
            self.__version[2] = 0
        elif level == 'minor':
            self.__version[1] += 1
            self.__version[2] = 0
        elif level == 'patch':
            self.__version[2] += 1
        else:
            raise ValueError("Error, invalid level: '{}', "
                             "should be major|minor|patch.".format(level))

        return self.__version

    def is_larger_then(self, other_version):
        """
        return True if current version is higher the 'other',
        :param other_version: PybumpVersion object
        :return: boolean
        """
        return self.__version > other_version.version

    def is_valid_semantic_version(self):
        return self.__valid_sem_ver

    def print_invalid_version(self):
        print("Invalid semantic version format: {}\n"
              "Make sure to comply with https://semver.org/ "
              "(lower case 'v' prefix is allowed)".format(self.__invalid_version),
              file=stderr)


def get_pypi_package_releases(package_name):
    """
    calls PYPI json api as described here
    https://wiki.python.org/moin/PyPIJSON
    https://warehouse.readthedocs.io/api-reference/json.html
    :param package_name: string, pypi project name
    :return: json with pypi project response
    """
    import requests

    result = requests.get('https://pypi.org/pypi/{}/json'.format(package_name))
    if result.status_code != 200:
        print('error occurred fetching package {} from PYPI.\n'
              'response is: {}'.format(package_name, result.reason))
        raise requests.exceptions.RequestException
    return result.json()


def is_patchable(x, y):
    """
    takes two lists, and checks if second list is patchable,
    a version is patchable only if major and minor values equal but patch value is higher in first version, for example:
    x = [0, 4, 8] y = [0, 4, 6] returns True
    x = [0, 4, 5] y = [0, 4, 6] returns False
    x = [2, 1, 1] y = [2, 4, 1] returns False
    :param x: list of ints
    :param y: list of ints
    :return: boolean
    """
    return x[0] == y[0] and x[1] == y[1] and x[2] > y[2]


def identify_possible_patch(releases_list, version_to_patch):
    """
    check if there is a possible patch version (in releases_list) newer then version_to_patch,
    get list of semantic versions,
    for example ['0.1.2', '0.1.3', '0.3.1', '0.3.2'] and 'version_to_patch' with PybumpVersion object

    :param releases_list: list of strings
    :param version_to_patch: PybumpVersion object
    :return: dict in the form of:
        {'patchable': boolean, 'latest_patch': 'string'}
    """
    if not releases_list or not version_to_patch:
        raise ValueError('one of the lists empty')

    # assume version_to_patch is the latest version
    latest_patch_version = version_to_patch
    patchable = False

    for release in releases_list:
        release_patch_candidate = PybumpVersion(release)

        if not release_patch_candidate.is_valid_semantic_version():
            # current 'release' does not meet semantic version, skip
            continue

        # check if version_to_patch is patchable
        if not is_patchable(release_patch_candidate.version, version_to_patch.version):
            continue

        # at this point possible patch version found, so if version_to_patch is [0, 3, 1],
        # and current iteration over releases_list is [0, 3, 2] then it matches for a patch,
        # but there also might be a release with version [0, 3, 3] and even newer, we need to find most recent.
        # calculate highest value found for patch (for cases when the 'releases' is not sorted)
        if release_patch_candidate.version[2] > latest_patch_version.version[2]:
            latest_patch_version = release_patch_candidate

    if latest_patch_version.is_larger_then(version_to_patch):
        patchable = True

    return {'patchable': patchable, 'latest_patch': latest_patch_version.__str__()}


def get_setup_py_install_requires(content):
    """
    Extract 'install_requires' value using regex from 'content',
    function will return a list of python packages:
    ['package_a', 'package_b==1.5.6', 'package_c>=3.0']

    :param content: the content of a setup.py file
    :return: list on strings, install_requires values as list
    """
    # use DOTALL https://docs.python.org/3/library/re.html#re.DOTALL to include new lines
    regex_install_requires_pattern = re.compile(r"install_requires=(.*?)],", flags=re.DOTALL)
    version_match = regex_install_requires_pattern.findall(content)

    if len(version_match) > 1:
        raise RuntimeError("More than one 'install_requires' found: {0}".format(version_match))
    if not version_match:
        # 'install_requires' missing from setup.py file, just return empty array
        return []

    # add ending ']' since regex will not include it
    found_install_requires = version_match[0] + ']'

    # convert found_install_requires values into an array and return
    from ast import literal_eval
    return literal_eval(found_install_requires)


def get_versions_from_requirements(requirements_list):
    """
    as described here https://pip.pypa.io/en/stable/reference/pip_install/#example-requirements-file
    python versions requirement may appear in the form of:
    docopt == 0.6.1             # Version Matching. Must be version 0.6.1
    keyring >= 4.1.1            # Minimum version 4.1.1
    coverage != 3.5             # Version Exclusion. Anything except version 3.5
    pybump ~= 1.1               # Compatible release. Same as >= 1.1, == 1.*

    the function is interested only in exact version match (case '==')
    brake python requirements list, in the form of ['package_a', 'package_b==1.5.6', 'package_c>=3.0'],
    for example
    ['pyyaml==5.3.1', 'pybump', 'GitPython>=3.1']
    into more detailed dictionary containing package name and PybumpVersion
    :param requirements_list: list of strings
    :return: list of dicts in the form of:
        [
            {
                'package_name': 'pyyaml',
                'package_version': PybumpVersion
            },
            {
                'package_name': 'pybump',
                'package_version': PybumpVersion
            }
        ]
    """
    dependencies = []
    for req in requirements_list:
        # split name from version by all allowed operators
        package_array = re.split("==|>=|!=|~=", req)

        package_name = package_array[0].strip()
        if len(package_array) == 1:
            # if package has no locked version or has >= type for current package, of type 'package>=2.7' its invalid
            version = PybumpVersion('latest')
        else:  # else the object will have a (probably) valid semantic version
            version = PybumpVersion(package_array[1].strip())

            # in case the string after '==' is not semantic version return error
            # if not version.is_valid_semantic_version():
            #     raise RuntimeError("Current package '{0}', is not set with semantic version: '{1}', cannot promote"
            #                        .format(package_name, package_array[1]))

        # append current package
        dependencies.append({'package_name': package_name, 'package_version': version})

    return dependencies


def check_available_python_patches(setup_py_content=None):
    """
    get the content of setup.py file and return a list of dicts with possible patchable dependencies versions,
    return will be in the form of:
    [
        {'package_name': 'pyyaml', 'version': '5.3.1', 'patchable': False, 'latest_patch': '5.3.1'},
        {'package_name': 'GitPython', 'version': '3.1.7', 'patchable': True, 'latest_patch': '3.1.12'}
    ]
    :param setup_py_content: content of setup.py file
    :return: list of dicts
    """
    requirements_list = get_setup_py_install_requires(setup_py_content)
    requirements_versions = get_versions_from_requirements(requirements_list)

    patchable_packages_array = []
    for requirement in requirements_versions:
        if requirement.get('package_version').is_valid_semantic_version():
            package_name = requirement.get('package_name')
            # get current package info (as json) from pypi api
            package_releases = get_pypi_package_releases(package_name)
            # version_to_patch is a PybumpVersion object
            version_to_patch = requirement.get('package_version')

            # convert keys of the 'releases' dict, into a list (only version numbers),
            releases_list = package_releases.get('releases').keys()  # releases_list is a list of strings

            res = identify_possible_patch(releases_list, version_to_patch)  # check for possible patch

            patchable_packages_array.append(
                {
                    'package_name': package_name,
                    'version': str(version_to_patch),
                    'patchable': res.get('patchable'),
                    'latest_patch': res.get('latest_patch')
                }
            )

    return patchable_packages_array


def is_valid_helm_chart(content):
    """
    Check if input dictionary contains mandatory keys of a Helm Chart.yaml file,
    as documented here https://helm.sh/docs/topics/charts/#the-chartyaml-file
    :param content: parsed YAML file as dictionary of key values
    :return: True if dict contains mandatory values, else False
    """
    return all(x in content for x in ['apiVersion', 'name', 'version'])


def get_setup_py_version(content):
    """
    Extract 'version' value using regex from 'content'
    :param content: the content of a setup.py file
    :return: version value as string
    """
    version_match = regex_version_pattern.findall(content)
    if len(version_match) > 1:
        raise RuntimeError("More than one 'version' found: {0}".format(version_match))
    if not version_match:
        raise RuntimeError("Unable to find version string in: {0}".format(content))
    return version_match[0][1]


def set_setup_py_version(version, content):
    """
    Replace version in setup.py file using regex,
    g<1> contains the string left of version
    g<3> contains the string right of version
    :param version: string
    :param content: content of setup.py as string
    :return: content of setup.py file with 'version'
    """
    return regex_version_pattern.sub(r'\g<1>{}\g<3>'.format(version), content)


def get_self_version(dist_name):
    """
    Return version number of input distribution name,
    If distribution not found return not found indication
    :param dist_name: string
    :return: version as string
    """
    try:
        return get_distribution(dist_name).version
    except DistributionNotFound:
        return 'version not found'


def write_version_to_file(file_path, file_content, version, app_version):
    """
    Write the 'version' or 'appVersion' to a given file
    :param file_path: full path to file as string
    :param file_content: content of the file as string
    :param version: version to set as string
    :param app_version: boolean, if True then set the appVersion key
    """
    # Append the 'new_version' to relevant file
    with open(file_path, 'w') as outfile:
        filename, file_extension = os.path.splitext(file_path)
        if file_extension == '.py':
            outfile.write(set_setup_py_version(version, file_content))
        elif file_extension == '.yaml' or file_extension == '.yml':
            if app_version:
                file_content['appVersion'] = version
            else:
                file_content['version'] = version
            yaml.dump(file_content, outfile, default_flow_style=False)
        elif os.path.basename(filename) == 'VERSION':
            outfile.write(version)
        outfile.close()


def read_version_from_file(file_path, app_version):
    """
    Read the 'version' or 'appVersion' from a given file,
    note for return values for file_type are:
        python for .py file
        helm_chart for .yaml/.yml files
        plain_version for VERSION files
    :param file_path: full path to file as string
    :param app_version: boolean, if True return appVersion from Helm chart
    :return: dict containing file content, version and type as:
     {'file_content': file_content, 'version': current_version, 'file_type': file_type}
    """
    with open(file_path, 'r') as stream:
        filename, file_extension = os.path.splitext(file_path)

        if file_extension == '.py':  # Case setup.py files
            file_content = stream.read()
            current_version = get_setup_py_version(file_content)
            file_type = 'python'
        elif file_extension == '.yaml' or file_extension == '.yml':  # Case Helm chart files
            try:
                file_content = yaml.safe_load(stream)
            except yaml.YAMLError as exc:
                print(exc)
            # Make sure Helm chart is valid and contains minimal mandatory keys
            if is_valid_helm_chart(file_content):
                file_type = 'helm_chart'
                if app_version:
                    current_version = file_content.get('appVersion', None)

                    # user passed the 'app-version' flag, but helm chart file does not contain the 'appVersion' field
                    if not current_version:
                        raise ValueError(
                            "Could not find 'appVersion' field in helm chart.yaml file: {}".format(file_content)
                        )
                else:
                    current_version = file_content['version']
            else:
                raise ValueError("Input file is not a valid Helm chart.yaml: {0}".format(file_content))
        else:  # Case file name is just 'VERSION'
            if os.path.basename(filename) == 'VERSION':
                # A version file should ONLY contain a valid semantic version string
                file_content = None
                current_version = stream.read()
                file_type = 'plain_version'
            else:
                raise ValueError("File name or extension not known to this app: {}{}"
                                 .format(os.path.basename(filename), file_extension))

    return {'file_content': file_content, 'version': current_version, 'file_type': file_type}


def main():
    parser = argparse.ArgumentParser(description='Python version bumper')
    subparsers = parser.add_subparsers(dest='sub_command')

    parser.add_argument('--version', action='version',
                        version='%(prog)s {}'.format(get_self_version('pybump')),
                        help='Print version and exit')
    parser.add_argument('--verify', required=False,
                        help='Verify if input string is a valid semantic version')

    # Define parses that is shared, and will be used as 'parent' parser to all others
    base_sub_parser = argparse.ArgumentParser(add_help=False)
    base_sub_parser.add_argument('--file', help='Path to Chart.yaml/setup.py/VERSION file', required=True)
    base_sub_parser.add_argument('--app-version', action='store_true',
                                 help='Bump Helm chart appVersion, relevant only for Chart.yaml files', required=False)

    # Sub-parser for bump version command
    parser_bump = subparsers.add_parser('bump', parents=[base_sub_parser])
    parser_bump.add_argument('--level', choices=['major', 'minor', 'patch'], help='major|minor|patch', required=True)
    parser_bump.add_argument('--quiet', action='store_true', help='Do not print new version', required=False)

    # Sub-parser for set version command
    parser_set = subparsers.add_parser('set', parents=[base_sub_parser])

    # Set mutual exclusion https://docs.python.org/3/library/argparse.html#mutual-exclusion,
    # To make sure that at least one of the mutually exclusive arguments is required
    set_group = parser_set.add_mutually_exclusive_group(required=True)
    set_group.add_argument('--auto', action='store_true',
                           help='Set automatic release / metadata from current git branch for current version')
    set_group.add_argument('--set-version',
                           help='Semantic version to set as a combination of \'vX.Y.Z-release+metadata\'')
    parser_set.add_argument('--quiet', action='store_true', help='Do not print new version', required=False)

    # Sub-parser for get version command
    parser_get = subparsers.add_parser('get', parents=[base_sub_parser])
    parser_get.add_argument('--sem-ver', action='store_true', help='Get the main version only', required=False)
    parser_get.add_argument('--release', action='store_true', help='Get the version release only', required=False)
    parser_get.add_argument('--metadata', action='store_true', help='Get the version metadata only', required=False)

    # Sub-parser for version latest patch verification command
    subparsers.add_parser('patch-verification', parents=[base_sub_parser])

    args = vars(parser.parse_args())

    # Case where no args passed, sub_command is mandatory
    if args['sub_command'] is None:
        if args['verify']:
            version = PybumpVersion(args['verify'])
            if version.is_valid_semantic_version():
                print('{} is valid'.format(version.__str__()))
            else:
                version.print_invalid_version()
                exit(1)
        else:
            parser.print_help()
        exit(0)

    # Read current version from the given file
    file_data = read_version_from_file(args['file'], args['app_version'])
    file_content = file_data.get('file_content')
    file_type = file_data.get('file_type')
    version_object = PybumpVersion(file_data.get('version'))

    if not version_object.is_valid_semantic_version():
        version_object.print_invalid_version()
        exit(1)

    if args['sub_command'] == 'patch-verification':
        if file_type == 'python':
            print(check_available_python_patches(setup_py_content=file_content))
        else:
            print('currently only python pypi packages supported for latest patch verifications')
            exit(1)
    elif args['sub_command'] == 'get':
        if args['sem_ver']:
            # Join the array of current_version_dict by dots
            print('.'.join(str(x) for x in version_object.version))
        elif args['release']:
            print(version_object.release)
        elif args['metadata']:
            print(version_object.metadata)
        else:
            print(version_object.__str__())
    else:
        # Set new_version to be invalid first
        new_version = None

        # Set the 'new_version' value
        if args['sub_command'] == 'set':
            # Case set-version argument passed, just set the new version with its value
            if args['set_version']:
                new_version = PybumpVersion(args['set_version'])
            # Case the 'auto' flag was set, set release with current git branch name and metadata with hash
            elif args['auto']:
                from git import Repo, InvalidGitRepositoryError
                # get the directory path of current working file
                file_dirname_path = os.path.dirname(args['file'])
                try:
                    repo = Repo(path=file_dirname_path)
                    # update current version release and metadata with relevant git values
                    version_object.release = repo.active_branch.name
                    version_object.metadata = str(repo.active_branch.commit)
                    new_version = version_object
                except InvalidGitRepositoryError:
                    print("{} is not a valid git repo".format(file_dirname_path), file=stderr)
                    exit(1)
            # Should never reach this point due to argparse mutual exclusion, but set safety if statement anyway
            else:
                print("set-version or auto flags are mandatory", file=stderr)
                exit(1)
        else:  # bump version ['sub_command'] == 'bump'
            # Only bump value of the 'version' key
            version_object.bump_version(args['level'])
            new_version = version_object
        # new_version should never be None at this point, but check this anyway
        if not new_version or not new_version.is_valid_semantic_version():
            new_version.print_invalid_version()
            exit(1)
        # Write the new version with relevant content back to the file
        write_version_to_file(args['file'], file_content, new_version.__str__(), args['app_version'])

        if args['quiet'] is False:
            print(new_version)


if __name__ == "__main__":
    main()
