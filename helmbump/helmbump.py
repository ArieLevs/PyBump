
import argparse
import yaml


def is_chart_file(content):
    return all(x in content for x in ['apiVersion', 'appVersion', 'description', 'name', 'version'])


def is_semantic_version(semantic_string):
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
    if level == 'major':
        version_array[0] += 1
    elif level == 'minor':
        version_array[1] += 1
    elif level == 'patch':
        version_array[2] += 1
    else:
        raise ValueError("Missed to validate level, invalid level: '{}'.".format(level))

    return version_array


def main():
    parser = argparse.ArgumentParser(description='Helm Charts version bumper')
    parser.add_argument('--file', help='Path to Chart.yaml file', required=True)
    parser.add_argument('--level', choices=['major', 'minor', 'patch'], help='major|minor|patch', required=True)
    parser.add_argument('--quiet', action='store_true', help='Do not print new version', required=False)
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

    current_version_array = is_semantic_version(current_version)
    if not current_version_array:
        print("Invalid semantic version format: {}".format(current_version))
        exit(1)

    new_version_array = bump_version(current_version_array, args['level'])
    new_version = '.'.join(str(x) for x in new_version_array)

    chart_yaml['version'] = new_version

    with open(args['file'], 'w') as outfile:
        yaml.dump(chart_yaml, outfile)
    outfile.close()

    if args['quiet'] is False:
        print(new_version)


if __name__ == "__main__":
    main()
