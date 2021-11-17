prettyip
========

Pretty-print IPy_'s IPSets in a human-readable fashion.

.. image:: https://coveralls.io/repos/djmitche/prettyip/badge.svg?branch=master
  :target: https://coveralls.io/r/djmitche/prettyip?branch=master

.. image:: https://travis-ci.org/djmitche/prettyip.svg?branch=master
  :target: https://travis-ci.org/djmitche/prettyip

Compatibility
-------------

Everywhere IPy_ runs, so does this -- CPython-2.6 through 3.4.

Usage
-----

Explicitly::

    from IPy import IPSet, IP
    import prettyip

    my_ipset = IPSet([IP('10.0.0.0/8')]) - IPSet([IP('10.0.1.2')])
    print(prettyip.pretty_ipset(my_ipset))

Or, monkey-patch IPy_::

    import prettyip

    prettyip.patch_ipy()

    my_ipset = IPSet([IP('10.0.0.0/8')]) - IPSet([IP('10.0.1.2')])
    print(my_ipset)

Results
-------

Simple IPs:

::

     >>> prettyip.pretty_ipset(IPSet([IP('10.0.0.0/8')]))
    '10.0.0.0/8'

Ranges:

::

    >>> IPSet([IP('10.120.13.11'), IP('10.120.13.12/30'), IP('10.120.13.16')])
    IPSet([IP('10.120.13.11'), IP('10.120.13.12/30'), IP('10.120.13.16')])
    >>> prettyip.pretty_ipset(_)
    '10.120.13.1{1-6}'

Big netblocks with smaller pieces missing:

::

     >>> IPSet([IP('1.0.0.0/8')]) - IPSet([IP('1.0.1.0/24')]) - IPSet([IP('1.0.9.0/24')])
     IPSet([IP('1.0.0.0/24'), IP('1.0.2.0/23'), IP('1.0.4.0/22'),
        IP('1.0.8.0/24'), IP('1.0.10.0/23'), IP('1.0.12.0/22'), IP('1.0.16.0/20'),
        IP('1.0.32.0/19'), IP('1.0.64.0/18'), IP('1.0.128.0/17'),
        IP('1.1.0.0/16'), IP('1.2.0.0/15'), IP('1.4.0.0/14'), IP('1.8.0.0/13'),
        IP('1.16.0.0/12'), IP('1.32.0.0/11'), IP('1.64.0.0/10'),
        IP('1.128.0.0/9')])
     >>> prettyip.pretty_ipset(_)
    '1.0.0.0/8 except 1.0.1.0/24, 1.0.9.0/24'

.. _IPy: https://pypi.python.org/pypi/IPy
