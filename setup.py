import setuptools

with open("README.rst", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="helmbump",
    version="0.1.0",
    author="Arie Lev",
    author_email="levinson.arie@gmail.com",
    description="Helm charts version bumper",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ArieLevs/HelmVersionBump",
    packages=setuptools.find_packages(),
    classifiers=(
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ),
    entry_points={
        'console_scripts': [
            'helmbump = helmbump.helmbump:main'
        ],
    },
)
