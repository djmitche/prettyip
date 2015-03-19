# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import os

_representers = []
_representer = _representers.append


@_representer
def singleton_ipset(ipset):
    if len(ipset.prefixes) == 1:
        yield (1.0, str(ipset.prefixes[0]))
    elif len(ipset.prefixes) == 0:
        yield (0.0, 'empty')


@_representer
def _range(ipset):
    if len(ipset.prefixes) == 0:
        return

    range = None
    ranges = []
    for pfx in ipset.prefixes:
        pfx_int = pfx.int()
        if range is None or pfx_int != range[1] + 1:
            range = [pfx_int, pfx_int + len(pfx) - 1]
            ranges.append(range)
        else:
            range[1] += len(pfx)

    def fmtrange(start, end):
        start, end = str(IP(start)), str(IP(end))
        if start == end:
            return start
        prefix = os.path.commonprefix([start, end])
        pfxlen = len(prefix)
        start, end = start[pfxlen:], end[pfxlen:]
        return '{}{{{}-{}}}'.format(prefix, start, end)

    yield (len(ranges),
           # TODO: format these better when they have a common prefix
           ", ".join(fmtrange(s, e) for s, e in ranges))

# TODO: sets on class boundaries
# TODO: inversions

@_representer
def _repr(ipset):
    yield (1000.0, str(ipset))


def _representations_for(ipset):
    for representer in _representers:
        for score, rep in representer(ipset):
            yield score, rep


def pretty_ipset(ipset):
    best = None
    best_score = None
    for score, rep in _representations_for(ipset):
        print "considering %r with score %r" % (rep, score)
        if score < best_score or best_score is None:
            best = rep
            best_score = score

    return best

from IPy import IPSet, IP
print pretty_ipset(IPSet([IP('10.0.0.3'), IP('10.0.0.4/31'), IP('10.0.0.8/29'), IP('10.0.0.7')]))
print pretty_ipset(IPSet([IP('10.0.0.15'), IP('10.0.0.16/31'), IP('10.0.0.18'), IP('10.0.0.7')]))
