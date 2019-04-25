
import argparse
import yaml
import re
import os
from pkg_resources import get_distribution, DistributionNotFound


regex_version_pattern = re.compile(r"((?:__)?version(?:__)? ?= ?[\"'])(.+?)([\"'])")


def is_valid_helm_chart(content):
    """
    Check if input dictionary contains mandatory keys of a Helm Chart.yaml file
    :param content: parsed YAML file as dictionary of key values
    :return: True if dict contains mandatory values, else False
    """
    return all(x in content for x in ['apiVersion', 'appVersion', 'description', 'name', 'version'])


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
    \g<1> contains the string left of version 
    \g<3> contains the string right of version 
    :param version: string
    :param content: content of setup.py as string
    :return: content of setup.py file with 'version'
    """
    return regex_version_pattern.sub('\g<1>{}\g<3>'.format(version), content)


def is_semantic_string(semantic_string):
    """
    Check if input string is a semantic version of type x.y.z
    Function will validate if each of x,y,z is an integer
    Will return [x, y, z] if True
    :param semantic_string: string
    :return: int array if True, else False
    """
    if type(semantic_string) != str:
        return False

    try:
        semantic_array = [int(n) for n in semantic_string.split('.')]
    except ValueError:
        return False

    if len(semantic_array) != 3:
        return False

    for index in semantic_array:
        if index not in range(0, 100000):
            return False

    return semantic_array


def bump_version(version_array, level):
    """
    Perform ++1 action on the array [x, y, z] cell,
    Input values are assumed to be validated
    :param version_array: int array of [x, y, z] validated array
    :param level: string represents major|minor|patch
    :return: int array with new value
    """
    if type(version_array) != list:
        raise ValueError("Error, invalid version_array: '{}', "
                         "should be [x, y, z].".format(version_array))

    if level == 'major':
        version_array[0] += 1
        version_array[1] = 0
        version_array[2] = 0
    elif level == 'minor':
        version_array[1] += 1
        version_array[2] = 0
    elif level == 'patch':
        version_array[2] += 1
    else:
        raise ValueError("Error, invalid level: '{}', "
                         "should be major|minor|patch.".format(level))

    return version_array


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


def main():
    parser = argparse.ArgumentParser(description='Python version bumper')
    subparsers = parser.add_subparsers(dest='sub_command')

    parser.add_argument('--version', action='version',
                        version='%(prog)s {}'.format(get_self_version('pybump')),
                        help='Print version and exit')

    # Sub-parser for bump version command
    parser_bump = subparsers.add_parser('bump')
    parser_bump.add_argument('--file', help='Path to Chart.yaml/setup.py file', required=True)
    parser_bump.add_argument('--level', choices=['major', 'minor', 'patch'], help='major|minor|patch', required=True)
    parser_bump.add_argument('--quiet', action='store_true', help='Do not print new version', required=False)

    # Sub-parser for set version command
    parser_set = subparsers.add_parser('set')
    parser_set.add_argument('--file', help='Path to Chart.yaml/setup.py file', required=True)
    parser_set.add_argument('--set-version', help='Semantic version to set as \'x.y.z\'', required=True)
    parser_set.add_argument('--quiet', action='store_true', help='Do not print new version', required=False)

    # Sub-parser for get version command
    parser_get = subparsers.add_parser('get')
    parser_get.add_argument('--file', help='Path to Chart.yaml/setup.py file', required=True)

    args = vars(parser.parse_args())

    # Case where no args passed, sub_command is mandatory
    if args['sub_command'] is None:
        parser.print_help()
        exit(0)

    current_version = ""
    setup_py_content = ""
    chart_yaml = {}

    with open(args['file'], 'r') as stream:
        filename, file_extension = os.path.splitext(args['file'])

        if file_extension == '.py':
            setup_py_content = stream.read()
            current_version = get_setup_py_version(setup_py_content)
        elif file_extension == '.yaml' or file_extension == '.yml':
            try:
                chart_yaml = yaml.load(stream)
            except yaml.YAMLError as exc:
                print(exc)

            if is_valid_helm_chart(chart_yaml):
                current_version = chart_yaml['version']
            else:
                raise ValueError("Input file is not a valid Helm chart.yaml: {0}".format(chart_yaml))
        else:
            raise ValueError("File extension is not known to this app: {0}".format(file_extension))

    current_version_array = is_semantic_string(current_version)
    if not current_version_array:
        print("Invalid semantic version format: {}".format(current_version))
        exit(1)

    if args['sub_command'] == 'get':
        print(current_version)
    else:
        # Set the 'new_version' value
        if args['sub_command'] == 'set':
            set_version = args['set_version']
            new_version = is_semantic_string(set_version)
            if not new_version:
                print("Invalid semantic version format: {}".format(set_version))
                exit(1)
            new_version = set_version
        else:  # bump version ['sub_command'] == 'bump'
            new_version_array = bump_version(current_version_array, args['level'])
            new_version = '.'.join(str(x) for x in new_version_array)

        # Append the 'new_version' to relevant file
        with open(args['file'], 'w') as outfile:
            if file_extension == '.py':
                outfile.write(set_setup_py_version(new_version, setup_py_content))
            elif file_extension == '.yaml' or file_extension == '.yml':
                chart_yaml['version'] = new_version
                yaml.dump(chart_yaml, outfile, default_flow_style=False)
            outfile.close()

        if args['quiet'] is False:
            print(new_version)


if __name__ == "__main__":
    main()
