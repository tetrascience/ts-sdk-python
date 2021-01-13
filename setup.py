# coding: utf-8

import sys
from setuptools import setup, find_packages

NAME = "ts-sdk"
VERSION = "1.0.0"
# To install the library, run the following
#
# python setup.py install
#
# prerequisite: setuptools
# http://pypi.python.org/pypi/setuptools

# Should we import info from requirements.txt ???
REQUIRES = [
    "attrs>=20.2.0,<21",
    "boto3>=1.16.3,<2",
    "botocore>=1.19.3,<2",
    "certifi>=2020.6.20,<2021",
    "chardet>=3.0.4,<4",
    "idna>=2.10,<3",
    "importlib-metadata>=2.0.0,<3",
    "jmespath>=0.10.0,<1",
    "jsonschema>=3.2.0,<4",
    "pyrsistent>=0.17.3,<1",
    "python-dateutil>=2.8.1,<3",
    "query-string>=2020.7.1,<2021",
    "requests>=2.24.0,<3",
    "s3transfer>=0.3.3,<1",
    "six>=1.15.0,<2",
    "smart-open[s3]>=3.0.0,<4",
    "typing-extensions>=3.7.4,<4",
    "urllib3>=1.25.11,<2",
    "zipp>=3.3.1,<4"
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
