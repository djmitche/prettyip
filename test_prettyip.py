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
    with patched_representations_for():
        global current_representer
        current_representer = fn
        try:
            yield
        finally:
            current_representer = None


@contextlib.contextmanager
def patched_representations_for():
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

        yield (t, s('0.0.0.0/0') - s('172.16.2.0/24'),
               [(100.9, '0.0.0.0/0 except reps_for(172.16.2.0/24)')])

        yield (t, s('10.132.30.0/24') - s('10.132.30.90') - s('10.132.30.96'),
               [(100.9, '10.132.30.0/24 except reps_for(10.132.30.90, 10.132.30.96)')])


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

    # a big mess..
    yield i, s('10.132.48.0/29', '10.132.48.8/30', '10.132.48.12/31',
            '10.132.48.14', '10.132.48.17', '10.132.48.18', '10.132.48.20/30',
            '10.132.48.24/29', '10.132.48.32/27', '10.132.48.64/26',
            '10.132.48.128/25', '10.132.49.0/29', '10.132.49.8/30',
            '10.132.49.12/31', '10.132.49.14', '10.132.49.16/31',
            '10.132.49.18',
            '10.132.49.20/30', '10.132.49.24/29', '10.132.49.32/27',
            '10.132.49.64/26', '10.132.49.128/27', '10.132.49.160/30',
            '10.132.49.164', '10.132.49.166/31', '10.132.49.168/29',
            '10.132.49.176/28', '10.132.49.192/26', '10.132.50.0/23',
            '10.134.48.0/28', '10.134.48.17', '10.134.48.18',
            '10.134.48.20/30',
            '10.134.48.24/29', '10.134.48.32/27', '10.134.48.64/27',
            '10.134.48.96/28', '10.134.48.112/30', '10.134.48.116/31',
            '10.134.48.119', '10.134.48.120', '10.134.48.122/31',
            '10.134.48.124/30', '10.134.48.128/25', '10.134.49.0/28',
            '10.134.49.16/31', '10.134.49.18', '10.134.49.20/30',
            '10.134.49.24/29', '10.134.49.32/27', '10.134.49.65',
            '10.134.49.66/31', '10.134.49.68/30', '10.134.49.72/29',
            '10.134.49.80/28', '10.134.49.96/27', '10.134.49.128/25',
            '10.134.50.0/23', '10.134.100.0/25', '10.134.100.128/27',
            '10.134.100.160/28', '10.134.100.176/29', '10.134.100.184/30',
            '10.134.100.188/31', '10.134.100.190', '10.134.100.192/26'), \
        ('10.132.0.0/14 except 10.132.{0.0-47.255}, 10.132.48.15/27, '
                '10.132.48.19, 10.132.49.15, 10.132.49.19, 10.132.49.165, '
                '10.13{2.52.0-4.47.255}, 10.134.48.16, 10.134.48.19, '
                '10.134.48.118, 10.134.48.121, 10.134.49.19, 10.134.49.64, '
                '10.134.{52.0-99.255}, 10.134.100.191, '
                '10.13{4.101.0-5.255.255}')


def test_patched():
    prettyip.patch_ipy()
    eq_(str(s('1.0.0.0/25', '1.0.0.128/25')), '1.0.0.0/24')


def test_format_range():
    eq_(prettyip.fmtrange(16, 16), (0.25, '0.0.0.16'))
    eq_(prettyip.fmtrange(0, 2 ** 1 - 1), (0.5, '0.0.0.0/31'))
    eq_(prettyip.fmtrange(16, 31), (0.5, '0.0.0.16/28'))
    eq_(prettyip.fmtrange(0, 2 ** 32 - 1), (0.5, '0.0.0.0/0'))
    eq_(prettyip.fmtrange(
        IP('10.0.0.0').int(),
        IP('11.0.0.0').int(),
        ),
        (5.0, '1{0.0.0.0-1.0.0.0}'))


def test_make_ip():
    ip = prettyip.mkip(16777216, 8)
    eq_(ip._prefixlen, 8)
    eq_(str(ip), '1.0.0.0/8')


def test_ipset():
    ipset = s()
    ip = prettyip.mkip(0, 0)
    eq_(prettyip.ipset_in_ip(ipset, ip), True)
    ipset = s('0.0.0.0/0')
    ip = prettyip.mkip(0, 1)
    eq_(prettyip.ipset_in_ip(ipset, ip), False)
    ipset = s('0.0.0.0/1')
    ip = prettyip.mkip(0, 1)
    eq_(prettyip.ipset_in_ip(ipset, ip), True)
    ipset = s('0.0.0.0/1', '128.0.0.0/1')
    ip = prettyip.mkip(0, 1)
    eq_(prettyip.ipset_in_ip(ipset, ip), False)


def test_smallest():
    ipset = s()
    eq_(prettyip.find_smallest(ipset), IP('0.0.0.0/24'))
    ipset = s('0.0.0.0/0')
    eq_(prettyip.find_smallest(ipset), IP('0.0.0.0/0'))
    ipset = s('0.0.0.0/1')
    eq_(prettyip.find_smallest(ipset), IP('0.0.0.0/1'))
    ipset = s('0.0.0.0/1', '128.0.0.0/1')
    eq_(prettyip.find_smallest(ipset), IP('0.0.0.0/0'))
    ipset = s('32.0.0.0/3', '64.0.0.0/3')
    eq_(prettyip.find_smallest(ipset), IP('0.0.0.0/1'))
