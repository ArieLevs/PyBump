import setuptools
from pkg_resources import parse_requirements

with open("requirements.txt") as f:
    requirements = [str(r) for r in parse_requirements(f)]

with open("README.rst", "r") as fh:
    long_description = fh.read()

keywords = ['bump', 'version', 'appVersion', 'versioning', 'helm', 'charts', 'setup.py', 'promote']

setuptools.setup(
    name="pybump",
    version="1.11.2",
    author="Arie Lev",
    author_email="levinsonarie@gmail.com",
    description="Python version bumper",
    keywords=keywords,
    long_description=long_description,
    long_description_content_type="text/x-rst",
    url="https://github.com/ArieLevs/PyBump",
    license='Apache License 2.0',
    packages=setuptools.find_packages(),
    install_requires=requirements,
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
    entry_points={
        'console_scripts': [
            'pybump = src.pybump:main'
        ],
    },
)
