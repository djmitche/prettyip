# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

# based on https://github.com/pypa/sampleproject

from setuptools import setup

import os.path

setup(
    name='prettyip',
    version='1.0.0',
    description="Pretty-print IPy's IPSets ",
    long_description=open(os.path.join(os.path.dirname(__file__), 'README.rst')).read(),
    url='https://github.com/djmitche/prettyip',
    author='Dustin J. Mitchell',
    author_email='dustin@mozilla.com',
    license='MPLv2',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Topic :: System :: Networking',
        'Topic :: Internet',
        'License :: OSI Approved :: Mozilla Public License 2.0 (MPL 2.0)',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
    ],
    keywords='ipy ip pretty-print',
    py_modules=['prettyip', 'test_prettyip'],
    install_requires=['IPy'],
    extras_require={
        'test': ['nose', 'mock'],
    },
)
