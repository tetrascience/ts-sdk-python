# coding: utf-8

import sys
from setuptools import setup, find_packages

NAME = "ts-sdk-python"
VERSION = "1.0.0"
# To install the library, run the following
#
# python setup.py install
#
# prerequisite: setuptools
# http://pypi.python.org/pypi/setuptools

REQUIRES = [
    "boto3",
    "jsonschema",
    "typing-extensions",
    "query-string",
    "smart-open",
    "requests",
    "importlib-metadata",
    "urllib3"
    ]

setup(
    name=NAME,
    version=VERSION,
    description="",
    author_email="",
    url="",
    keywords=[],
    install_requires=REQUIRES,
    packages=find_packages(),
    include_package_data=True,
    long_description=""
)
