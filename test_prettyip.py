# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import mock
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
    with patched_reresentations_for():
        global current_representer
        current_representer = fn
        try:
            yield
        finally:
            current_representer = None


@contextlib.contextmanager
def patched_reresentations_for():
    """Patch representations_for so that it does not recurse to other
    representers but returns a fixed string"""
    with mock.patch('prettyip.representations_for') as reps_for:
        def fake(ipset, ignore=None):
            ipstrs = ', '.join(str(ip) for ip in ipset.prefixes)
            yield (99.9, 'reps_for({0})'.format(ipstrs))
        reps_for.side_effect = fake
        yield reps_for


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
    with representer(prettyip.dashed_range):
        yield (t, s('1.0.0.3', '1.0.0.4/31', '1.0.0.6'),
               [(1.0, '1.0.0.{3-6}')])

        yield (t, s('1.0.0.0/24') - s('1.0.0.0'),
               [(1.0, '1.0.0.{1-255}')])

        # a singleton in the middle
        yield (t, s('1.0.0.0/24') - s('1.0.0.17') - s('1.0.0.19'),
               [(3.25, '1.0.0.{0-16}, 1.0.0.18, 1.0.0.2{0-55}')])

        # a range encompassing all digits, with a very bad score
        yield (t, s('0.0.0.0/5', '8.0.0.0/8', '9.0.0.0/8'),
               [(104.0, '{0.0.0.0-9.255.255.255}')])

        # CIDR range
        yield (t, s('1.0.0.0/24') - s('1.0.0.128'),
               [(1.5, '1.0.0.0/25, 1.0.0.{129-255}')])


def test_except_for():
    with representer(prettyip.except_for):
        yield (t, s('1.0.0.0/20') - s('1.0.1.128'),
               [(100.9, '1.0.0.0/20 except reps_for(1.0.1.128)')])

        yield (t, s('1.0.0.0/17') + s('1.0.128.0/17') - s('1.0.1.128'),
               [(100.9, '1.0.0.0/16 except reps_for(1.0.1.128)')])


def test_prefix_list():
    with representer(prettyip.prefix_list):
        yield (t, s('1.0.0.0/24', '2.0.0.0/15', '3.0.0.0/8'),
               [(30.0, '1.0.0.0/24, 2.0.0.0/15, 3.0.0.0/8')])


def test_integration():
    def i(input, output):
        eq_(prettyip.pretty_ipset(input), output)
    yield i, s(), 'nothing'
    for bits in range(0, 32):
        yield i, s('0.0.0.0/{0}'.format(bits)), '0.0.0.0/{0}'.format(bits)
    yield i, s('1.0.0.0/8'), '1.0.0.0/8'
    yield i, s('1.2.0.0/16'), '1.2.0.0/16'
    yield i, s('1.2.3.0/24'), '1.2.3.0/24'
    yield i, s('1.2.3.4'), '1.2.3.4'  # no /32 suffix
    yield i, s('1.0.0.0/20') - s('1.0.1.128'), \
        '1.0.0.0/20 except 1.0.1.128'
    yield i, s('1.0.0.0/8') - s('1.0.1.0/24') - s('1.0.9.0/24'), \
        '1.0.0.0/8 except 1.0.1.0/24, 1.0.9.0/24'
    yield i, s('1.0.0.0/8') - s('1.15.0.0/16') + s('1.15.20.0/24'), \
        '1.0.0.0/8 except 1.15.{0.0-19.255}, 1.15.2{1.0-55.255}'


def test_patched():
    prettyip.patch_ipy()
    eq_(str(s('1.0.0.0/25', '1.0.0.128/25')), '1.0.0.0/24')
