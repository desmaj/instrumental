Using instrumental
==================

Running instrumental
--------------------

instrumental provides a command that will run your Python code in an environment in which it can measure code execution characteristics. Using it looks like this::

  instrumental <path to your python script>

When you run your code this way, it should run and exit as normal. instrumental will have gathered coverage information, but because you haven't asked for a report it won't tell you anything about it. 

Statement coverage
------------------

Try this::

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

Condition / decision coverage
-----------------------------

instrumental also aims to provide more rigorous forms of code coverage. Try running instrumental like this::

  instrumental -r -t pyramid -i pyramid.tests `which nosetests`

Invoking instrumental this way executes your code and provides you with a condition/decision coverage report
when execution is complete. The output should look something like this::

  ===============================================
  Instrumental Condition/Decision Coverage Report
  ===============================================
  
  Decision -> pyramid.authentication:43 < logger >
  
  T ==> True
  F ==> False
  
  ...
  
  Decision -> pyramid.view:31 < (package_name is None) >
  
  T ==> True
  F ==> False
  
  LogicalOr -> pyramid.view:281 < (getattr(request, 'exception', None) or context) >
  
  T * ==> True
  F T ==> False
  F F ==> False

The preceeding output is formatted like this::

  <construct type> -> <modulename>.<line number> < <source code> >
  
  <description of result>

So in the example report above, the first chunk tells us that for the decision on line 43 of pyramid.authentication, 
the False case was never executed. So we can say that test, evaluating "logger", never ran when "logger" evaluated
not-True. Likewise, the second chunk tells us that the code at line 31 in pyramid.view was never executed when
package_name was not None.

The third chunk in the example report describes the condition coverage for the logical or on line 281 of
pyramid.view. The result there says that every time the or decision was executed, the expression on the left side
always evaluated True as a boolean expression. So the expression on the right side of the or, context, was never
tested!
