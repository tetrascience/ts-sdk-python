# coding: utf-8

import os
from setuptools import setup, find_packages

REQUIRES = [
    "boto3>=1.16.3,<2",
    "botocore>=1.19.3,<2",
    "jsonschema>=3.2.0,<4",
    "query-string>=2020.7.1,<2021",
    "requests>=2.22.0,<3",
    "smart-open[s3]>=3.0.0,<4",
    "typing-extensions>=3.7.4,<4"
    ]

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

if 'CI' in os.environ and not 'TRAVIS_TAG' in os.environ:
    version = f'1.0.dev{os.environ.get("TRAVIS_BUILD_ID")}'
else:
    version = os.environ.get('TRAVIS_TAG', 'local.dev')

setup(
    name="ts-sdk",
    version=version,
    description="Tetrascience Python SDK",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="tetrascience",
    author_email="developers@tetrascience.com",
    url="https://developers.tetrascience.com",
    keywords=[],
    install_requires=REQUIRES,
    packages=find_packages(),
    package_data={'': ['*.txt', '*.json', '*.template', '*.md', '*.py']},
    include_package_data=True,
    python_requires='>=3.7',
    entry_points={
        'console_scripts': {
            'ts-sdk = ts_sdk.cli.__main__:main'
        }
    },
    license='Apache License 2.0'
)
