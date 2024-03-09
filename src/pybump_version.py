import re
from sys import stderr


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
        search a match according to the regular expression, so for example '1.1.2-prerelease+meta' is valid,
        then make sure there is and exact single match and validate if each of x,y,z is an integer.

        in case a non-valid version passed, 'valid_sem_ver' will stay False

        param version: string
        """
        orig_version = version
        # only if passed version is non-empty string
        if isinstance(version, str) and len(version) != 0:
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
        # re-validate that updated version with new release is still valid
        self.validate_semantic_string(self.__str__())

    @property
    def metadata(self):
        return self.__metadata

    @metadata.setter
    def metadata(self, value):
        # re-validate that updated version with new metadata is still valid
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
