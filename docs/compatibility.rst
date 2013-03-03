Compatibility
=============

coverage.py
-----------

There is one major code coverage tool available in the Python world, `coverage.py <http://nedbatchelder.com/code/coverage>`_. coverage.py is a powerful and mature tool that provides both statement and branch coverage information for almost any running Python code. It's a great tool; you should use it if you don't use instrumental and maybe even if you do.

instrumental aims to be compatible with coverage.py use patterns wherever possible. Currently this means supporting the '# pragma: no cover' tag, producing a cobertura-compatible xml coverage report, and producing a colorful html coverage report. So theoretically, instrumental should be easy to fit into a process that currently uses coverage.py.
