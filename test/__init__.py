# make sure to import package directory whe running tests from root dir
import os
import sys

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
sys.path.append(os.path.join(ROOT, 'src'))

valid_helm_chart = {'apiVersion': 'v1',
                    'appVersion': '1.0',
                    'description': 'A Helm chart for Kubernetes',
                    'name': 'test',
                    'version': '0.1.0'}
invalid_helm_chart = {'apiVersion': 'v1',
                      'notAppVersionKeyHere': '1.0',
                      'description': 'A Helm chart for Kubernetes',
                      'version': '0.1.0'}
empty_helm_chart = {}

# setup.py is missing the install_requires=[] key
valid_setup_py = """
    setuptools.setup(
        name="pybump",
        version="0.1.3",
        author="Arie Lev",
        author_email="levinsonarie@gmail.com",
        description="Python version bumper",
        long_description=long_description,
        long_description_content_type="text/markdown",
        url="https://github.com/ArieLevs/PyBump",
        license='Apache License 2.0',
        packages=setuptools.find_packages(),
    )
    """

valid_setup_py_2 = """
    setuptools.setup(
        name="pybump",
        version="0.1.3",
        author="Arie Lev",
        author_email="levinsonarie@gmail.com",
        description="Python version bumper",
        long_description=long_description,
        long_description_content_type="text/markdown",
        url="https://github.com/ArieLevs/PyBump",
        license='Apache License 2.0',
        install_requires=[
            "pyyaml",
            "pybump==1.3.3"
        ],
        packages=setuptools.find_packages(),
    )
    """

# This setup.py content is missing 'version' key
# and 'install_requires' key is wrongly set to 'installation_requires'
invalid_setup_py_1 = """
    setuptools.setup(
        name="pybump",
        invalid_version_string="0.1.3",
        author="Arie Lev",
        author_email="levinsonarie@gmail.com",
        description="Python version bumper",
        installation_requires=[
            "pyyaml",
            "pybump==1.3.3"
        ],
    )
    """

# This setup.py content 'version' key declared 3 times
# and 'install_requires' key declared twice
invalid_setup_py_multiple_ver = """
    setuptools.setup(
        name="pybump",
        version="0.1.3",
        version="0.1.2",
        __version__="12356"
        author="Arie Lev",
        author_email="levinsonarie@gmail.com",
        description="Python version bumper",
        install_requires=[
            "pyyaml",
            "pybump==1.3.3"
        ],
        install_requires=[
            "pyyaml",
            "pybump==1.3.3"
        ],
    )
    """

valid_pyproject_toml = """
    [project]
    name = "test-project"
    version = "0.1.0"
    description = "description"
    readme = "README.md"
    requires-python = ">=3.13"
    dependencies = []
    """

# pyproject.toml with compound keys containing 'version' substring (issue #58)
# Should only match 'version = "2.0.0"' and NOT 'target-version' or other compound keys
valid_pyproject_toml_with_compound_keys = """
[project]
name = "test-project"
version = "2.0.0"
description = "A test project"

[tool.ruff]
target-version = "py312"

[tool.some]
this-is-a-version-containing-key = "1.1.7"
myversion = "should-not-match"
"""

# Content with version NOT at line start - should still match (inline in setup.py style)
valid_setup_py_inline_version = """
    setuptools.setup(
        name="pybump",
        version="3.2.1",
        author="Test",
    )
    """

valid_version_file_1 = """0.12.4"""
valid_version_file_2 = """1.5.0-alpha+meta"""
invalid_version_file_1 = """
    this is some text in addition to version
    1.5.0
    nothing except semantic version should be in this file
    """
invalid_version_file_2 = """
    version=1.5.0
    """
