#! /bin/bash

set -e

VERSION=$1

grep $VERSION setup.py || {
    echo "version not in setup.py"
    exit 1
}

git tag $VERSION
rm dist/*
python setup.py sdist bdist_wheel
twine upload -s dist/*
