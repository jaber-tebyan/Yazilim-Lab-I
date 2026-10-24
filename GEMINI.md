I use specific pattern in writing code in this project.
There are patterns like:

1. Rules
2. Interfaces
3. Tests

In rules there is no modification of state, only they can either return Error code only or return error code | some result that is right now used in the tests.
And in fact depending on that tests will either use the Generic Result which is Ok, Err or they will just create the object and do their test.
Interfaces are only for state changes or returning something that is heavily used in the project or the GUI may need it as well.

As for tests then it is known their pattern.
