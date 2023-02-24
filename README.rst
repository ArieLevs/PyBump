=====================
Python Version Bumper
=====================
.. image:: https://github.com/arielevs/pybump/workflows/Python%20package/badge.svg
    :alt: Build
    :target: https://pypi.org/project/pybump/

.. image:: https://codecov.io/gh/ArieLevs/PyBump/branch/master/graph/badge.svg?token=P3AZKGX5IR
    :alt: Code Coverage
    :target: https://codecov.io/gh/ArieLevs/PyBump

.. image:: https://img.shields.io/pypi/v/pybump.svg
    :alt: Version
    :target: https://pypi.org/project/pybump/

.. image:: https://img.shields.io/pypi/l/pybump.svg?colorB=blue
    :alt: License
    :target: https://pypi.org/project/pybump/

.. image:: https://img.shields.io/pypi/pyversions/pybump.svg
    :alt: Python Version
    :target: https://pypi.org/project/pybump/

| Simple python code to bump kubernetes package manager Helm charts.yaml, VERSION and setup.py files versions. 
| Versions must match semver 2.0.0: https://github.com/semver/semver/blob/master/semver.md
| Version is allowed a lower case 'v' character for example: ``v1.5.4-beta2``

Install
=======
``pip install pybump``

Usage
=====

| **bump** version:
| ``pybump bump [-h] --file PATH_TO_CHART.YAML --level {major,minor,patch} [--quiet]``
|

| **set** explicit version or set auto release+metadata:
| ``pybump set --file PATH_TO_CHART.YAML --set-version X.Y.Z [--quiet]``
|
| the **auto** flag is mainly intended for pull request CIs, by using:
| ``pybump set --file PATH_TO_CHART.YAML --auto [--quiet]``
| pybump will add git commit hash as release info to version

 * NOTE - This can be dangerous as the `auto` flag might detect a git repo you were not intended to bump,
   make sure the bumped file is really a child in the git repo you intended to bump.

| **get** current version:
| ``pybump get --file PATH_TO_CHART.YAML``
|

| update Helm chart **appVersion**:
| in order to bump/get/set the Helm chart appVersion value just add the ``--app-version`` flag
| ``pybump bump [-h] --file PATH_TO_CHART.YAML --level {major,minor,patch} [--quiet] [--app-version]``

 * note that the --app-version flag is relevant only for Helm chart.yaml files and has not effect on other cases.

Examples
========

CLI example
-------------

.. image:: ./docs/pybump-recording.gif


CI Usage example
----------------

Simple jenkins CI (using k8s plugin) that will use the `set --file setup.py --auto` options

..  code-block:: java

    String label = "test-bump-ci-runner"
    podTemplate(
            label: label,
            containers: [
                    containerTemplate(
                            name: 'pybump',
                            image: "arielev/pybump:1.10.2",
                            ttyEnabled: true,
                            command: 'sleep',
                            args: '1d'
                    ),
                    containerTemplate(
                            name: 'jnlp',
                            image: 'jenkins/inbound-agent:jdk11',
                            ttyEnabled: true
                    )
            ]
    ) {
        node(label) {
            timeout(time: 10, unit: 'MINUTES') {
                ansiColor('xterm') {
                    String version = ""
                    container('jnlp') {
                        git credentialsId: "credentials_id_here", url: "https://github.com/arielevs/pybump"
                    }
                    container('pybump') {
                        version = sh(
                                script: "pybump set --file setup.py --auto",
                                returnStdout: true
                        ).trim()
                    }
                    println(version)
                }
            }
        }
    }

| Case: ``version: 0.0.1``
| ``pybump bump --file Chart.yaml --level patch`` will bump version to ``0.0.2``
|

| Case: ``version: 0.1.4-alpha+meta.data``
| ``pybump bump --file Chart.yaml --level minor`` will bump version to ``0.2.0-alpha+meta.data``
|

| Case: ``version: v0.0.3``
| ``pybump bump --file Chart.yaml --level major`` will bump version to ``v1.0.0``
|

| Case: ``version: 0.0.1+some-metadata``
| ``pybump set --file Chart.yaml --set-version 1.4.0`` will set version to ``1.4.0+metadata-here``
|

| Case: ``version: v7.0.2``
| ``pybump set --file setup.py --auto`` will set version to ``v7.0.2-5a51e0e1d9894d3c5d4201619f10be242320cb59``
|

| Case: ``appVersion 2.3.2``
| ``pybump bump --file Chart.yaml --level patch --app-version`` will bump appVersion to ``2.3.3``
|

| Case: ``version: 1.0.13``
| ``pybump get --file Chart.yaml`` will return ``1.0.13``
|

| Case: ``version: 1.0.13+some-metadata``
| ``pybump get --file Chart.yaml --release`` will return ``some``

using a container image
-----------------------
| ``docker run --rm --volume $(pwd):/tmp -t arielev/pybump set --file /tmp/setup.py --auto``
|