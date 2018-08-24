Helm Version Bump
=================

Simple python code to bump kubernetes package manager Helm charts version.

Usage
-----
**bump** version:
``helmbump bump [-h] --file PATH_TO_CHART.YAML --level {major,minor,patch} [--quiet]``

**set** explicit version:
``helmbump set --file PATH_TO_CHART.YAML --set-version X.Y.Z [--quiet]``

**get** current version:
``helmbump get --file PATH_TO_CHART.YAML``


Examples
--------

Case: ``version: 0.0.1``
``helmbump bump --file Chart.yaml --level patch`` will bump version to ``version: 0.0.2``


Case: ``version: 0.1.4``
``helmbump bump --file Chart.yaml --level minor`` will bump version to ``version: 0.2.0``


Case: ``version: 0.0.1``
``helmbump set --file Chart.yaml --set-version 1.4.0`` will bump version to ``version: 1.4.0``
