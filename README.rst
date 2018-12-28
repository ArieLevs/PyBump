Python Version Bumper
=====================

.. image:: https://img.shields.io/pypi/v/pybump.svg
    :alt: Version
    :target: https://pypi.org/project/pybump/

.. image:: https://img.shields.io/pypi/l/pybump.svg?colorB=blue
    :alt: License
    :target: https://pypi.org/project/pybump/

.. image:: https://img.shields.io/pypi/pyversions/pybump.svg
    :alt: Python Version
    :target: https://pypi.org/project/pybump/

Simple python code to bump kubernetes package manager Helm charts and setup.py versions.

Install
-------
``pip install pybump``

Usage
-----
**bump** version:
``pybump bump [-h] --file PATH_TO_CHART.YAML --level {major,minor,patch} [--quiet]``

**set** explicit version:
``pybump set --file PATH_TO_CHART.YAML --set-version X.Y.Z [--quiet]``

**get** current version:
``pybump get --file PATH_TO_CHART.YAML``


Examples
--------

Case: ``version: 0.0.1``
``pybump bump --file Chart.yaml --level patch`` will bump version to ``version: 0.0.2``


Case: ``version: 0.1.4``
``pybump bump --file Chart.yaml --level minor`` will bump version to ``version: 0.2.0``


Case: ``version: 0.0.1``
``pybump set --file Chart.yaml --set-version 1.4.0`` will set version to ``version: 1.4.0``
