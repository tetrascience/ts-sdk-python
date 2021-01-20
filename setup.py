# coding: utf-8

import os
from setuptools import setup, find_packages

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

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="ts-sdk",
    version=os.environ.get('TRAVIS_TAG', 'local.dev'),
    description="Tetrascience Python SDK",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="tetrascience",
    author_email="developers@tetrascience.com",
    url="https://developers.tetrascience.com",
    keywords=[],
    install_requires=REQUIRES,
    packages=find_packages(),
    package_data={'': ['*.txt', '*.json']},
    include_package_data=True,
    python_requires='>=3.7',
    license='Apache License 2.0'
)
