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
    name="pybump",
    version="1.12.6",
    author="Arie Lev",
    author_email="levinsonarie@gmail.com",
    description="Python version bumper",
    keywords=keywords,
    long_description=long_description,
    long_description_content_type="text/x-rst",
    url="https://github.com/ArieLevs/PyBump",
    license='Apache License 2.0',
    packages=setuptools.find_packages(),
    install_requires=parse_requirements("requirements.txt"),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
    entry_points={
        'console_scripts': [
            'pybump = src.pybump:main'
        ],
    },
)
