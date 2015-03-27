#! /bin/bash

set -e

VERSION=$1
if test -z "$VERSION"; then
    echo "Give the version"
    exit 1
fi

git tag $VERSION
rm -rf dist/*
python setup.py sdist bdist_wheel
twine upload -s dist/*
