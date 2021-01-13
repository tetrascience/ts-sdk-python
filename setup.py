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

# Should we import info from requirements.txt ???
REQUIRES = [
    "attrs>=20.2.0",
    "boto3>=1.16.3",
    "botocore>=1.19.3",
    "certifi>=2020.6.20",
    "chardet>=3.0.4",
    "idna>=2.10",
    "importlib-metadata>=2.0.0",
    "jmespath>=0.10.0",
    "jsonschema>=3.2.0",
    "pyrsistent>=0.17.3",
    "python-dateutil>=2.8.1",
    "query-string>=2020.7.1",
    "requests>=2.24.0",
    "s3transfer>=0.3.3",
    "six>=1.15.0",
    "smart-open[s3]>=3.0.0",
    "typing-extensions>=3.7.4.3",
    "urllib3>=1.25.11",
    "zipp>=3.3.1"
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
