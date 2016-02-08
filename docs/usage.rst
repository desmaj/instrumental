Using instrumental
==================

Running instrumental
--------------------

instrumental provides a command that will run your Python code in an environment in which it can measure code execution characteristics. Using it looks like this::

  $ instrumental <path to your python script>

When you run your code this way, it should run and exit as normal. instrumental will have gathered coverage information, but because you haven't asked for a report it won't tell you anything about it. 

Statement coverage
------------------

Try this::

  $ instrumental -S -t <packagename> <path to your python script>

The '-S' flag indicates that you want to see a statement coverage report and the '-t' flag tells instrumental that you want the package `packagename` instrumented and included in the coverage report.

While developing instrumental, I often run it against the pyramid tests (since they keep their coverage levels high). That looks something like this::

  $ instrumental -S -t pyramid -i pyramid.tests `which nosetests`

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

If there are statements that weren't executed during the instrumented run, instrumental will report their line numbers in the 'Missing' column of the statement coverage report.

Condition / decision coverage
-----------------------------

instrumental also aims to provide more rigorous forms of code coverage. Try running instrumental like this::

  $ instrumental -r -t pyramid -i pyramid.tests `which nosetests`

Invoking instrumental this way executes your code and provides you with a condition/decision coverage report
when execution is complete. The output should look something like this::

  ===============================================
  Instrumental Condition/Decision Coverage Report
  ===============================================
  
  Decision -> pyramid.authentication:43 < logger >
  
  T ==> X
  F ==> 
  
  ...
  
  Decision -> pyramid.view:31 < (package_name is None) >
  
  T ==> X
  F ==> 
  
  LogicalOr -> pyramid.view:281 < (getattr(request, 'exception', None) or context) >
  
  T * ==> X
  F T ==> 
  F F ==> 

The preceeding output is formatted like this::

  <construct type> -> <modulename>.<line number> < <source code> >
  
  <description of result>

So in the example report above, the first chunk tells us that for the decision on line 43 of pyramid.authentication, 
the False case was never executed. So we can say that test, evaluating "logger", never ran when "logger" evaluated
not-True. Likewise, the second chunk tells us that the code at line 31 in pyramid.view was never executed when
package_name was not None.

The third chunk in the example report describes the condition coverage for the logical or on line 281 of
pyramid.view. The result there says that every time the or decision was executed, the expression on the left side
always evaluated True as a boolean expression. So the expression on the right side of the or, 'context', was never
Tested!

Unreachable Cases
-----------------

There are times when you may include a literal in an expression. It may be in an assignment (as below) or in the test for an if statement. Instrumental doesn't judge. If Instrumental finds a decision that contains one or more literals it won't, by default, count against coverage totals the cases that are directly unreachable because of a literal. On the other hand, Instrumental will hold you responsible for cases that are unreachable due to the presence of literals proceeding them in the calcuation of the decision. A concrete example of this would probably be helpful here.

Note that in the following report section, the literal value '/' is used as the second condition in the decision. So the 'F F' condition combination will never be possible and is considered unreachable. In this situation, Instrumental will only expect the 'T *' and 'F T' condition combinations to be reported as covered. As long as those combinations are seen during execution, this decision is considered to be fully covered and it will not be present in the coverage report.::

  LogicalOr -> pyramid.view:277.1 < (request.environ['PATH_INFO'] or '/') >
  
  ** One or more condition combinations may not be reachable due to the presence of a literal in the decision
  
  T * ==> X
  F T ==> X
  F F ==> U

Now consider the decision described in the next report chunk. This is the same expression as the one in the last example except that it has an additional condition at the end. In this situation, Instrumental will recognize that the 'F F T' and 'F F F' combinations are unreachable, but only the 'F F F' combination is marked as unreachable and so exempted from coverage. This is because the literal in the expression prevents the final condition, 'default_path()', from ever being evaluated. Since this represents a possible bug, Instrumental will report it as missed coverage.::

  LogicalOr -> pyramid.view:277.1 < (request.environ['PATH_INFO'] or '/' or default_path()) >
  
  ** One or more condition combinations may not be reachable due to the presence of a literal in the decision
  
  T * * ==> X
  F T * ==> X
  F F T ==>  
  F F F ==> U

If you're interested in expressions that contain literals, you can always use the --report-literals option. This option tells Instrumental to count cases that are unreachable due to the presence of literals during coverage calculation.

Marking conditions as unreachable
---------------------------------

It may be that there are condition combinations that aren't possible, but appear possible to Instrumental. In this situation you can tell Instrumental to not expect to find certain condition combinations using the 'pragma: no cond' directive. Let's look at a concrete example::

  [1] a = func1()
  [2] b = False
  [3] c = func2()
  [4] if a or b or c: # pragma: no cond(F T F)
  [5]     func3()
  [6] else:
  [7]     func4()

In this example we can see that the 'F T F' case will not ever be possible since b will always be False. We can communicate this to instrumental by adding a comment to the end of line 4 in the form "pragma: no cond(<condition1>[,condition2, ..., conditionN])". When we do that, Instrumental will output something like the following::

  LogicalOr -> somemodule:4.1 < (a or b or c) >
  
  T * * ==> 
  F T * ==> P
  F F T ==>  
  F F F ==> 

In this report chunk, the 'P' indicates that the 'F T F' condition combination has been marked as impossible by a pragma. If we wanted to also say that the 'F F T' case we impossible, our pragma would look more like, "pragma: no cond(F T F,F F T)". The "pragma: no cond" system also supports nested expressions. Consider the following modified code::

  [1] a = func1()
  [2] b = True
  [3] c = func2()
  [4] if a or (b and d) or c: # pragma: no cond[.2](F T)
  [5]     func3()
  [6] else:
  [7]     func4()

Here we can see that the impossible condition will be the 'F T' combination in the nested 'and'. You can indicate that the pragma applies to the nested 'and' by specifying a "selector" of [.2]. The .2 will match the label that Instrumental will give the expression (i.e. 4.2) and Instrumental will know which expression to apply the pragma to. You can even add the pragma on a separate line and specify a selector that contains a line number. In this case, you could add the comment, "# pragma: no cond[4.2](F T)" to line 3 and Instrumental would figure out that the pragma should be applied to the expression labeled 4.2.

Excluding expressions from instrumentation
------------------------------------------

In order to do the things it does, Instrumental takes some liberties with your code. This doesn't always work out very well with a language as dynamic as Python. Comparison operations are a good case to loo at. Instrumental, by default, attempts to detect comparisons and modify them so that it can measure the result of their executions as either True or False. But Python allows you to replace the semantics of comparisons with your own if you'd like. So comparisons may not evaluate to True or False at all. It is for this case that Instrumental provides --ignore-comparisons. Specifying the --ignore-comparisons option on the command-line tells instrumental to not touch comparisons at all. So you'll lose the ability to measure the execution of comparisons, but at least they won't raise exceptions or give you other problems.

Instrumental also instruments and reports on the expressions in assertions by default. This can result in noisy missed condition reports since the expressions evaluated in the context of assertions are usually expected to be True for all cases. This is why Instrumental provides the --ignore-assertions option. Specifying --ignore-assertions on the command-line tells Instrumental to leave those assertions alone and not report on the results of evaluating them.

Gathering coverage over multiple runs
-------------------------------------

In some cases, running your tests may mean running several actualy test runs. Then you'll want to produce a coverage result for each run and combine then all into one file that you can report on. Instrumental now support this!

You can now run instrumental with the -l (or --label) option turned on. Instrumental will give the coverage file it produces a (probably) unique filename each time it runs. Then you can use the instrumental-tools to combine the coverage files into one file that you can report on.

Here's an example session illustrating the use of the -l option and instrumental-tools command::

  [1] $ instrumental -l -t yourpackage test_things.py
  [2] $ instrumental -l -t yourpackage test_more_things.py
  [3] $ ls -a1
      .
      ..
      .instrumental.p1111.cov
      .instrumental.p2222.cov
       ...
      yourpackage
  [4] $ instrumental-tools combine .instrumental.cov .instrumental.p*.cov
  [5] $ instrumental -r

Commands [1] and [2] each run some tests in a different process. Command [3] checks to see what the names of the created coverage files are. We can see that the files .instrumental.p1111.cov and .instrumental.p2222.cov were created. Command [4] uses the instrumental-tools combine command to combine coverage files matching the pattern `.instrumental.p*.cov` into the file `.instrumental.cov`. Then command [5] runs instrumental and asks for a report on the coverage file. Command [5] is a little tricky since it counts on the generated coverage file being called `.instrumental.cov` because that's the default coverage file name. If we had specified a different coverage file name in command [4], like my.cov, then command [5] would look more like::

  [5] $ instrumental -f my.cov -r

