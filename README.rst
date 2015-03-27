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
    print prettyip(my_ipset)

Or, monkey-patch IPy_::

    import prettyip

    prettyip.patch_ipy()

    my_ipset = IPSet([IP('10.0.0.0/8')]) - IPSet([IP('10.0.1.2')])
    print my_ipset

.. _IPy: https://pypi.python.org/pypi/IPy
