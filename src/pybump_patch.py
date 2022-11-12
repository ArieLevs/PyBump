import re
from pybump_version import PybumpVersion


class PybumpPatchableVersion(object):
    def __init__(self, package_name, version):
        self.__package_name = package_name
        self.__version = version
        self.patchable = False
        self.latest_patch = None

    @property
    def package_name(self):
        return self.__package_name

    @property
    def version(self):
        return self.__version

    def identify_possible_patch(self, releases_list):
        """
        check if there is a possible patch version (in releases_list) newer than self.__version,
        get list of semantic versions, for example ['0.1.2', '0.1.3', '0.3.1', '0.3.2']

        param releases_list: list of strings
        """
        if not releases_list:
            raise ValueError('releases_list cannot be empty')

        # assume self.__version is the latest version
        latest_patch_version = self.__version

        for release in releases_list:
            release_patch_candidate = PybumpVersion(release)

            if not release_patch_candidate.is_valid_semantic_version():
                # current 'release' does not meet semantic version, skip
                continue

            # check if version_to_patch is patchable
            if not self.is_patchable(release_patch_candidate.version, self.__version.version):
                continue

            # at this point possible patch version found, so if version_to_patch is [0, 3, 1],
            # and current iteration over releases_list is [0, 3, 2] then it matches for a patch,
            # but there also might be a release with version [0, 3, 3] and even newer, we need to find most recent.
            # calculate the highest value found for patch (for cases when the 'releases' is not sorted)
            if release_patch_candidate.version[2] > latest_patch_version.version[2]:
                latest_patch_version = release_patch_candidate

        if latest_patch_version.is_larger_then(self.__version):
            self.patchable = True
        else:
            self.patchable = False
        self.latest_patch = latest_patch_version

    def get_dict(self):
        return {
            "package_name": self.package_name,
            "version": str(self.version),
            "patchable": self.patchable,
            "latest_patch": str(self.latest_patch)
        }

    def __str__(self):
        return str(self.get_dict())

    @staticmethod
    def is_patchable(x, y):
        """
        takes two lists, and checks if second list is patchable,
        a version is patchable only if major and minor values equal but patch value is higher in first version,
        for example:
        x = [0, 4, 8] y = [0, 4, 6] returns True
        x = [0, 4, 5] y = [0, 4, 6] returns False
        x = [2, 1, 1] y = [2, 4, 1] returns False
        :param x: list of ints
        :param y: list of ints
        :return: boolean
        """
        return x[0] == y[0] and x[1] == y[1] and x[2] > y[2]


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


def get_setup_py_install_requires(content):
    """
    Extract 'install_requires' value using regex from 'content',
    function will return a list of python packages:
    ['package_a', 'package_b==1.5.6', 'package_c>=3.0']

    param content: the content of a setup.py file
    :return: list of strings, install_requires values as list
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
    as described here https://pip.pypa.io/en/stable/reference/requirement-specifiers/#requirement-specifiers
    python versions requirement may appear in the form of:
    docopt == 0.6.1             # Version Matching. Must be version 0.6.1
    keyring >= 4.1.1            # Minimum version 4.1.1
    coverage != 3.5             # Version Exclusion. Anything except version 3.5
    pybump ~= 1.1               # Compatible release. Same as >= 1.1, == 1.*

    the function is interested only in exact version match (case '=='), and will not consider '!=' patching
    brake python requirements list, in the form of ['package_a', 'package_b ==1.5.6', 'package_c>=  3.0 #   comment'],
    for example
    ['pyyaml==5.3.1', 'pybump', 'GitPython>=3.1']
    :param requirements_list: list of strings
    :return: list of PybumpPatchableVersion objects in the form of:
        [PybumpPatchableVersion, PybumpPatchableVersion, PybumpPatchableVersion, ]
    """
    dependencies = []
    for req in requirements_list:
        # a valid package requirement can be "GitPython  == 3.1.27 # comment here"
        # split name from version by all allowed operators
        package_array = re.split("==|>=|~=", req)

        if len(package_array) != 2:
            # if after split, a list that is not of type ["name", "ver"] returned, then the delimiter is not valid
            version = PybumpVersion('invalid')
        else:  # else the object will have a (probably) valid semantic version
            # the "ver" part can be like " 3.1.27 # comment here" with a comment
            # the semantic version also needs to get extracted
            raw_version = package_array[1].split("#")
            version = PybumpVersion(raw_version[0].strip())

        # get package name and strip all spaces so "GitPython  " becomes "GitPython"
        package_name = package_array[0].strip()

        # append current package
        dependencies.append(PybumpPatchableVersion(package_name, version))

    return dependencies


def check_available_python_patches(requirements_list=None):
    """
    get list of python requirements and return a list of dicts with possible patchable dependencies versions,
    return will be in the form of:
    [
        {'package_name': 'pyyaml', 'version': '5.3.1', 'patchable': False, 'latest_patch': '5.3.1'},
        {'package_name': 'GitPython', 'version': '3.1.7', 'patchable': True, 'latest_patch': '3.1.12'}
    ]
    :param requirements_list: content of setup.py file
    :return: list of dicts
    """
    requirements_versions = get_versions_from_requirements(requirements_list)

    patchable_packages_array = []
    for requirement in requirements_versions:
        if requirement.version.is_valid_semantic_version():
            # get current package info (as json) from pypi api
            package_releases = get_pypi_package_releases(requirement.package_name)

            # convert keys of the 'releases' dict, into a list (only version numbers),
            releases_list = package_releases.get('releases').keys()  # releases_list is a list of strings
            requirement.identify_possible_patch(releases_list)
            patchable_packages_array.append(requirement.get_dict())

    return patchable_packages_array
