# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from IPy import IP, IPSet
import os

POWERS_OF_2 = dict((2 ** n, n) for n in range(0, 32 + 1))

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
def dashed_range(ipset):
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

    def fmtrange(start_int, end_int):
        # bail out early for singletons..
        if start_int == end_int:
            return 0.25, str(IP(start_int))
        # and for CIDR ranges
        bit_diff_exp = POWERS_OF_2.get((start_int ^ end_int) + 1)
        if bit_diff_exp is not None:
            return 0.5, '{0!s}/{1!s}'.format(IP(start_int), 32 - bit_diff_exp)
        # otherwise make a dashed range
        start, end = str(IP(start_int)), str(IP(end_int))
        prefix = os.path.commonprefix([start, end])
        pfxlen = len(prefix)
        start, end = start[pfxlen:], end[pfxlen:]
        # calculate th score for this range, penalizing for shorter
        # prefixes (longer dashed ranges) and for not ending on a dot
        score = 4.0 - prefix.count('.')
        if not prefix:
            # wrapping {..} around the whole ipset is not readable!
            score += 100.0
        elif prefix[-1] != '.':
            score += 1.0
        return score, '{0}{{{1}-{2}}}'.format(prefix, start, end)

    scored_formats = [fmtrange(s, e) for s, e in ranges]
    score = sum(range_score for (range_score, _) in scored_formats)
    yield score, ", ".join(range_fmt for (_, range_fmt) in scored_formats)


@representer
def except_for(ipset):
    # this isn't worth it for simple sets
    if len(ipset.prefixes) < 3:
        return

    def mkip(net, prefixlen):
        ip = IP(net)
        ip._prefixlen = prefixlen
        return ip

    def ipset_in_ip(ipset, ip):
        for prefix in ipset.prefixes:
            if prefix not in ip:
                return False
        return True

    lower = 0
    smallest_containing = None
    for bitlength in range(1, 24):
        low_half = mkip(lower, bitlength)
        # this doesn't work :(
        if ipset_in_ip(ipset, low_half):
            smallest_containing = low_half
            continue
        lower += 1 << (32 - bitlength)
        high_half = mkip(lower, bitlength)
        if ipset_in_ip(ipset, high_half):
            smallest_containing = high_half
            continue
        break

    # if we found a CIDR block containing the whole IPSet,
    # try inverting it
    if smallest_containing:
        prefix = "%s except " % (smallest_containing)
        inverted = IPSet([smallest_containing]) - ipset
        for score, rep in representations_for(inverted, ignore=[except_for]):
            yield score + 1, prefix + rep


@representer
def prefix_list(ipset):
    yield (10.0 * len(ipset.prefixes),
           ", ".join(str(ip) for ip in ipset.prefixes))


def representations_for(ipset, ignore=None):
    for representer in representers:
        if ignore and representer in ignore:
            continue
        for score, rep in representer(ipset):
            yield score, rep


def pretty_ipset(ipset):
    best = None
    best_score = None
    for score, rep in representations_for(ipset):
        if best_score is None or score < best_score:
            best = rep
            best_score = score

    return best


def patch_ipy():
    IPSet.__str__ = pretty_ipset
