# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from IPy import IP
import os

representers = []


def representer(fn):
    representers.append(fn)
    return fn


@representer
def singleton(ipset):
    if len(ipset.prefixes) == 1:
        yield (1.0, str(ipset.prefixes[0]))


@representer
def empty(ipset):
    if len(ipset.prefixes) == 0:
        yield (0.0, 'nothing')


@representer
def range(ipset):
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
        return '{0}{{{1}-{2}}}'.format(prefix, start, end)

    yield (len(ranges) + 1.0,
           # TODO: format these better when they have a common prefix
           ", ".join(fmtrange(s, e) for s, e in ranges))

# TODO: sets on class boundaries
# TODO: inversions


@representer
def _repr(ipset):
    yield (100.0, ", ".join(str(ip) for ip in ipset.prefixes))


def _representations_for(ipset):
    for representer in representers:
        for score, rep in representer(ipset):
            yield score, rep


def pretty_ipset(ipset):
    best = None
    best_score = None
    for score, rep in _representations_for(ipset):
        print("considering %r with score %r" % (rep, score))
        if best_score is None or score < best_score:
            best = rep
            best_score = score

    return best
