Helm Version Bump
=================

Simple python code to bump kubernetes package manager Helm charts version.

Usage
-----
bumping version:
``helmbump bump [-h] --file PATH_TO_CHART.YAML --level {major,minor,patch} [--quiet]``

set explicit version:
``helmbump set --file PATH_TO_CHART.YAML --set-version X.Y.Z [--quiet]``

get current version:
``helmbump get --file PATH_TO_CHART.YAML``
