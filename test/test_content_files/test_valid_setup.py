import setuptools

setuptools.setup(
    name="pybump",
    version="1.0.1-aa2cfd71788ab67bc9b59e62dee2070765948e29",
    author="Arie Lev",
    author_email="levinsonarie@gmail.com",
    description="Python version bumper",
    long_description="README.rst",
    long_description_content_type="text/markdown",
    url="https://github.com/ArieLevs/PyBump",
    license='Apache License 2.0',
    packages=setuptools.find_packages(),
    install_requires=[
        'pybump==1.3.1',
        'GitPython==3.1.7',
        'pyyaml>=5.2',
        'package_a',
        'package_b!=34.1.5',
    ],
)
