Using instrumental
==================

Running instrumental
--------------------

instrumental provides a command that will run your Python code in an environment in which it can measure code execution characteristics. Using it looks like this::

  instrumental <path to your python script>

When you run your code this way, it should run and exit as normal. instrumental will have gathered coverage information, but because you haven't asked for a report it won't tell you anything about it. Try this::

  instrumental -S -t <packagename> <path to your python script>

The '-S' flag indicates that you want to see a statement coverage report and the '-t' flag tells instrumental that you want the package `packagename` instrumented and included in the coverage report.

While developing instrumental, I often run it against the pyramid tests (since they keep their coverage levels high). That looks something like this::

  instrumental -S -t pyramid -i pyramid.tests `which nosetests`

There I'm telling instrumental to run nosetests targetting the 'pyramid' package, ignoring the 'pyramid.tests' package, and producing a statement coverage report.The results look something like this::

  =======================================
  Instrumental Statement Coverage Summary
  =======================================
  
  Name                          Stmts   Miss  Cover   Missing
  -----------------------------------------------------------
  pyramid                           5      0   100%   
  pyramid.asset                    30      0   100%   
  pyramid.authentication          325      0   100%   
  ...
  pyramid.view                    103      0   100%   
  pyramid.wsgi                     14      0   100%   
  -----------------------------------------------------------
  TOTAL                          6419      0   100%

