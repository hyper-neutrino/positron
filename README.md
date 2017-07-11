# positron
Positron Programming Language - Practical

To run, download all of the files into one directory and then run `python lang.py file.txt <arg1> <arg2> ...` to run a program.

## Requirements
`sympy` needs to be installed to run Positron.

# examples
A tutorial will be coming sometime, so for now, hopefully these examples offer some guidelines of how to use this programming language.

### datatypes
There are a few datatypes:

- numbers: these are represented by the `sympy` Python package to prevent floating point errors.
- strings: these are just Python strings
- lists: these are just Python lists
- tuples: these are just Python tuples, except when you pass them to a function, it will splat them automatically. To prevent this, use `((1, 2, 3),)` (i.e. wrapping it in an outer tuple)

### assignment
To assign a value to a symbol, use the `=` operator. For example, `x = 2` assigns `2` to the symbol `x`. `x = y = 2` will assign `2` to `y` and `y` to `x`, which will make both `x` and `y` equal `2`.

### functions
A function object looks like this:

  function {
    // Do something; arguments are $1, $2, ... with $0 being the whole list of arguments
  }

This can be treated like any other object, including being passed into other functions like in Python.

### conditionals
A conditional looks like this:

  if <condition> then {
    // Do something
  } elif <condition> then {
    // Do something
  } else {
    // Do something
  }

If `<condition>` is a simple statement, it doesn't need brackets around it, but sometimes it does. Unless you're using this language for code golf, use brackets anyway :P

### loops
A while loop looks like this:

  while <condition> do {
    // Do something
  }

A foreach loop looks like this:

  foreach <list> do {
    // Do something; $1 is the current element
  }

### function calls
Function calls are done like so: `function@argument`, or with multiple arguments, `function@(argument, argument, ...)`. To pass an actual tuple as one of the arguments, use `function@((content, content),)`. Note that `function@x` will splat the argument if `x` is a tuple, so only use tuples when that is the desired behavior; otherwise, use lists.
