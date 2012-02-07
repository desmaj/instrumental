Introduction
============

What is instrumental?
---------------------

instrumental is a structural coverage reporting tool. instrumental can tell you 
which parts of your program have been executed after it has been run. You can 
use this information to verify that your tests have executed your code and to
determine which code has not been tested.

What's the problem?
-------------------

Testing is hard. Writing test cases is the easy part (and it isn't always 
that easy). The hard part is determining which tests to write and which 
inputs to choose when you write those tests.

Let's say that your code contains an '''and''' decision that comprises three
conditions as inputs. Maybe your decision looks like this:

::

  (a == 4) and (b > 2) and c

We'll assume that the three conditions (a == 4, b > 2, and c (is not False))
are significant. This should be a safe assumption to make; if those
conditions don't significantly affect the result of your program then they
probably shouldn't be in the code in the first place.

Since these are significant conditions, it is important to test them
thoroughly. This means ensuring that there are tests that depend on each of
the conditions to force the decision result to a predictable value. The way
to do this is, when testing a particular condition, to hold the other
conditions that can affect the result of the decision to particular values.

These ideas should be starting to feel familiar. This is what we do when we
write unit tests; we isolate individual units so that we can verify their
behaviour without having to worry about any other code confounding the
results of our testing. So think of this as testing units within units.
It isn't possible to break the and decision into smaller functional units,
but the other conditions can be effectively removed from the equation by
holding them constant.

So then to test our first condition in our decision, a == 4, we'll need to
write at least two cases. We need one case in which a is 4 and one in which
it isn't. Further, we need to neutralize the other conditions. In the case
of an and decision we do this by holding the other input conditions to True.
This allows us to prove that if the result of the decision is True, then it
must have been a taking a value of 4 that caused it. We can similarly prove
that if the result of the decision is False then it must have been a taking
a value other than 4 that was the cause. The following table illustrates
input selections that do just this:

+---+---+------+
| a | b | c    |
+===+===+======+
| 4 | 3 | True |
+---+---+------+
| 5 | 3 | True |
+---+---+------+

Inputs that fully test this decision might look like this:

+---+---+-------+
| a | b | c     |
+===+===+=======+
| 4 | 3 | True  |
+---+---+-------+
| 5 | 3 | True  |
+---+---+-------+
| 4 | 2 | True  |
+---+---+-------+
| 4 | 3 | False |
+---+---+-------+

If we display this as the result of evaluating the individual conditions, we
get a table that looks like this:

+-------+-------+-------+
| True  | True  | True  |
+-------+-------+-------+
| False | True  | True  |
+-------+-------+-------+
| True  | False | True  |
+-------+-------+-------+
| True  | True  | False |
+-------+-------+-------+

You can see that we need a case where all conditions are True, and then we
'walk' the False across the conditions to get cases where the significant
condition forces the parent decision False.

This is a simple case, but you can see that the kind of analysis involved
here is non-trivial. When you extrapolate this to a realistic program, the
analysis quickly becomes prohibitively time-consuming and tedious. This is
where instrumental can help.

What does instrumental do?
--------------------------

instrumental executes your program for you. Upon completion, it can produce
a report indicating whether or not the significant cases for a decision were
executed.

What doesn't instrumental do?
-----------------------------

instrumental doesn't currently provide branch coverage. We are unlikely to provide
branch coverage any time soon since we provide decision coverage, a superset of branch coverage.
