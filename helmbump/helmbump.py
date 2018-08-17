
import argparse
import yaml


def is_chart_file(content):
    """
    Check if input dictionary contains mandatory keys of a Helm Chart.yaml file
    :param content: parsed YAML file as dictionary of key values
    :return: True is dict contains mandatory values, else False
    """
    return all(x in content for x in ['apiVersion', 'appVersion', 'description', 'name', 'version'])


def is_semantic_string(semantic_string):
    """
    Check if input string is a semantic version of type x.y.z
    Function will validate if each of x,y,z is an integer
    Will return [x, y, z] if True
    :param semantic_string: string
    :return: int array if True, else False
    """
    try:
        semantic_array = [int(n) for n in semantic_string.split('.')]
    except ValueError:
        return False

    if len(semantic_array) != 3:
        return False

    for index in semantic_array:
        if index not in range(0, 10000):
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
    if level == 'major':
        version_array[0] += 1
    elif level == 'minor':
        version_array[1] += 1
    elif level == 'patch':
        version_array[2] += 1
    else:
        raise ValueError("Missed level validation on start, invalid level: '{}'.".format(level))

    return version_array


def main():
    parser = argparse.ArgumentParser(description='Helm Charts version bumper')
    subparsers = parser.add_subparsers(dest='sub_command')

    # Sub-parser for bump version command
    parser_bump = subparsers.add_parser('bump')
    parser_bump.add_argument('--file', help='Path to Chart.yaml file', required=True)
    parser_bump.add_argument('--level', choices=['major', 'minor', 'patch'], help='major|minor|patch', required=True)
    parser_bump.add_argument('--quiet', action='store_true', help='Do not print new version', required=False)

    # Sub-parser for set version command
    parser_set = subparsers.add_parser('set')
    parser_set.add_argument('--file', help='Path to Chart.yaml file', required=True)
    parser_set.add_argument('--set-version', help='Semantic version to set as \'x.y.z\'', required=True)
    parser_set.add_argument('--quiet', action='store_true', help='Do not print new version', required=False)

    # Sub-parser for get version command
    parser_get = subparsers.add_parser('get')
    parser_get.add_argument('--file', help='Path to Chart.yaml file', required=True)

    args = vars(parser.parse_args())

    chart_yaml = {}
    with open(args['file'], 'r') as stream:
        try:
            chart_yaml = yaml.load(stream)
        except yaml.YAMLError as exc:
            print(exc)

    if is_chart_file(chart_yaml):
        current_version = chart_yaml['version']
    else:
        raise ValueError("Input file is not a valid Helm chart.yaml: {0}".format(chart_yaml))

    current_version_array = is_semantic_string(current_version)
    if not current_version_array:
        print("Invalid semantic version format: {}".format(current_version))
        exit(1)

    if args['sub_command'] == 'get':
        print(current_version)

    else:
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

        chart_yaml['version'] = new_version

        with open(args['file'], 'w') as outfile:
            yaml.dump(chart_yaml, outfile, default_flow_style=False)
            outfile.close()

        if args['quiet'] is False:
            print(new_version)


if __name__ == "__main__":
    main()
