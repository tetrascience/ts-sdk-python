#!/usr/bin/env sh

PATH=$(pyenv root)/shims:$PATH

rm -fr ./dist

pyenv local 3.7.9
python3 -m pip install wheel

./setup.py build bdist_wheel