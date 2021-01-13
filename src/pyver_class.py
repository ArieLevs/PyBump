
class PybumpVersion(object):
    prefix = False
    version = [0, 0, 0]
    release = None
    metadata = None

    def __init__(self, version_array, prefix=False, release=None, metadata=None):
        self.prefix = prefix
        self.version = version_array
        self.release = release
        self.metadata = metadata

    def __str__(self):
        """
        reconstruct version to string, if releases or metadata passed, override the one that is part of object
        :return: string
        """
        result_string = ''
        if self.prefix:
            result_string = 'v'
        result_string += '.'.join(str(x) for x in self.version)

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
            self.version[0] += 1
            self.version[1] = 0
            self.version[2] = 0
        elif level == 'minor':
            self.version[1] += 1
            self.version[2] = 0
        elif level == 'patch':
            self.version[2] += 1
        else:
            raise ValueError("Error, invalid level: '{}', "
                             "should be major|minor|patch.".format(level))

        return self.version

    def is_larger_then(self, other_version):
        """
        return True if current version is higher the 'other',
        :param other_version: PybumpVersion object
        :return: boolean
        """
        return self.version > other_version.version
