# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import contextlib
from nose.tools import eq_
from IPy import IP, IPSet

import prettyip

current_representer = None


def s(*ips):
    "Construct an IPSet from the given strings"
    return IPSet([IP(ip) for ip in ips])


def t(input, output):
    "Test the current representer with the given input and output"
    eq_(sorted(list(current_representer(input))), sorted(output))


@contextlib.contextmanager
def representer(fn):
    "Set the current representer"
    global current_representer
    current_representer = fn
    try:
        yield
    finally:
        current_representer = None


def test_singleton():
    with representer(prettyip.singleton):
        yield (t, s('1.2.3.0/24'),
               [(1.0, '1.2.3.0/24')])
        yield (t, s('1.2.3.0/24', '1.1.1.1'),
               [])


def test_empty():
    with representer(prettyip.empty):
        yield (t, s(),
            [(0.0, 'nothing')])
        yield (t, s('1.2.3.0/24', '1.1.1.1'),
            [])


def test_range():
    with representer(prettyip.range):
        yield (t, s('1.0.0.3', '1.0.0.4/31', '1.0.0.6'),
            [(2.0, '1.0.0.{3-6}')])

        yield (t, s('1.0.0.0/24') - s('1.0.0.0'),
            [(2.0, '1.0.0.{1-255}')])

        yield (t, s('1.0.0.0/24') - s('1.0.0.128'),
            [(3.0, '1.0.0.{0-127}, 1.0.0.{129-255}')])


def test_integration():
    def i(input, output):
        eq_(prettyip.pretty_ipset(input), output)
    yield i, s(), 'nothing'
    yield i, s('1.2.3.4'), '1.2.3.4'
    yield i, s('1.2.3.0/24'), '1.2.3.0/24'
