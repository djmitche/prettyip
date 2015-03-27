#! /bin/bash

set -e

VERSION=$1

git tag $VERSION
rm dist/*
python setup.py sdist bdist_wheel
twine upload -s dist/*
