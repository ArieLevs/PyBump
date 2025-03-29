import setuptools
from packaging.requirements import Requirement


def parse_requirements(filename):
    requirements_list = []
    with open(filename, 'r') as f:
        for line in f.readlines():
            line = line.strip()
            if line and not line.startswith("#"):  # Skip empty lines and comments
                try:
                    req = Requirement(line)  # Validate the requirement using packaging
                    requirements_list.append(str(req))
                except ValueError:
                    print(f"Invalid requirement line: {line}")
    return requirements_list


with open("README.rst", "r") as fh:
    long_description = fh.read()

keywords = ['bump', 'version', 'appVersion', 'versioning', 'helm', 'charts', 'setup.py', 'promote']

setuptools.setup(
    name="pybump"
)
