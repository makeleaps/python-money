#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

from setuptools.command.test import test as TestCommand

from version import get_git_version


loc = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(loc, "README.md")) as f:
    README = f.read()


class PyTest(TestCommand):
    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        # import here, cause outside the eggs aren't loaded
        import pytest

        errno = pytest.main(self.test_args)
        sys.exit(errno)


keywords = "money currency finance".split()

tests_require = [
    "pytest-django",
    "pytest-cov",
    "django<1.10",
    "psycopg2",
    "six",
]

requirements = [
    "six",
]

extras_require = {
    "django": [
        "Django<1.10",
    ],
}

dependency_links = []

setup(
    name="python-money",
    version=get_git_version(),
    description="Primitives for working with money and currencies in Python",
    url="http://github.com/poswald/python-money",
    maintainer="Paul Oswald",
    maintainer_email="pauloswald@gmail.com",
    license="BSD",
    platforms=["any"],
    keywords=keywords,
    long_description=README,
    packages=[
        "money",
    ],
    package_dir={"money": "money"},
    include_package_data=True,  # Read in MANIFEST.in
    zip_safe=False,
    install_requires=requirements,
    tests_require=tests_require,
    extras_require=extras_require,
    dependency_links=dependency_links,
    cmdclass={"test": PyTest},
    classifiers=[
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Topic :: Office/Business :: Financial",
    ],
)
