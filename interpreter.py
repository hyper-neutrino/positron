from tokenizer import *
from parser import *
from logger import *
import sympy, sys, os

"""

datatypes
---------
string
number
list
regex

"""

def getDefaultInterpreter():
    directory = os.path.dirname(os.path.realpath(__file__))
    interpreter = Interpreter(args = None, func_args = None, tree = None, symbolmap = {}, directory = directory)
    imports = interpreter.Import(directory, "core.pos", False)
    for key in imports:
        interpreter.symbolmap[key] = imports[key]
    imports = interpreter.PythonImport(directory, "core")
    for key in imports:
        interpreter.symbolmap[key] = imports[key]
    return interpreter

def _(ref, symbolmap):
    if hasattr(ref, "assign") and hasattr(ref, "value"):
        return ref.value
    elif type(ref) == type(IdentifierContainer("")):
        if str(ref) in symbolmap:
            return symbolmap[str(ref)]
        else:
            raise RuntimeError("Identifier %s is not defined" % str(ref))
    elif type(ref) == type(()):
        return tuple(_(child, symbolmap) for child in ref)
    else:
        return ref

def equ(ref1, ref2, symbolmap):
    ref1, ref2 = _(ref1, symbolmap), _(ref2, symbolmap)
    return [0, 1][ref1 == ref2]

def neq(ref1, ref2, symbolmap):
    return 1 - equ(ref1, ref2, symbolmap)

def gt(ref1, ref2, symbolmap):
    ref1, ref2 = _(ref1, symbolmap), _(ref2, symbolmap)
    return 1 if ref1 > ref2 else 0

def lt(ref1, ref2, symbolmap):
    ref1, ref2 = _(ref1, symbolmap), _(ref2, symbolmap)
    return 1 if ref1 < ref2 else 0

def geq(ref1, ref2, symbolmap):
    return gt(ref1, ref2, symbolmap) or equ(ref1, ref2, symbolmap)

def leq(ref1, ref2, symbolmap):
    return lt(ref1, ref2, symbolmap) or equ(ref1, ref2, symbolmap)

def subref(ref1, ref2, symbolmap):
    ref1 = _(ref1, symbolmap)
    if type(ref2) == type(IdentifierContainer("")):
        return ref1[ref2.name]
    else:
        raise RuntimeError("Invalid subreference")

def asn(ref1, ref2, symbolmap):
    ref2 = _(ref2, symbolmap)
    if hasattr(ref1, "assign") and hasattr(ref1, "value"):
        ref1.assign(ref2)
    else:
        if type(ref1) == type(IdentifierContainer("")):
            symbolmap[str(ref1)] = ref2
        elif type(ref1) == type(()):
            if type(ref2) in [type([]), type(())]:
                if len(ref1) > len(ref2):
                    raise RuntimeError("Not enough values to unpack")
                elif len(ref1) < len(ref2):
                    raise RuntimeError("Too many values to unpack")
                else:
                    for index in range(len(ref1)):
                        asn(ref1[index], ref2[index])
            else:
                raise RuntimeError("Type '%s' is not iterable" % str(type(ref2)))
        else:
            raise RuntimeError("Left-hand side of assignment must be a reference, not a value")
    return ref1 # TODO

def addasn(ref1, ref2, symbolmap):
    return asn(ref1, add(ref1, ref2, symbolmap), symbolmap)

def mnsasn(ref1, ref2, symbolmap):
    return asn(ref1, mns(ref1, ref2, symbolmap), symbolmap)

def modasn(ref1, ref2, symbolmap):
    return asn(ref1, mod(ref1, ref2, symbolmap), symbolmap)

def mulasn(ref1, ref2, symbolmap):
    return asn(ref1, mul(ref1, ref2, symbolmap), symbolmap)

def expasn(ref1, ref2, symbolmap):
    return asn(ref1, exp(ref1, ref2, symbolmap), symbolmap)

def divasn(ref1, ref2, symbolmap):
    return asn(ref1, div(ref1, ref2, symbolmap), symbolmap)

def get(ref1, ref2, symbolmap, actual = False):
    ref1, ref2 = _(ref1, symbolmap), _(ref2, symbolmap)
    if type(ref1) == type(""):
        return ref1[ref2]
    else:
        if actual and type(ref2) == type(()):
            return ref1.get(*ref2)
        else:
            return ref1.get(ref2)

def getdefault(ref, symbolmap):
    if type(_(ref, symbolmap)) == type(""):
        return list(_(ref, symbolmap))
    else:
        return _(ref, symbolmap).get()

def add(ref1, ref2, symbolmap):
    ref1, ref2 = _(ref1, symbolmap), _(ref2, symbolmap)
    if type(ref1) == type(ref2) and type(ref2) == type(Array([])):
        return Array(ref1.elements + ref2.elements)
    elif type(ref2) == type(Array([])):
        return Array([ref1 + element for element in ref2.elements])
    elif type(ref1) == type(Array([])):
        return Array([element + ref2 for element in ref1.elements])
    return ref1 + ref2 # TODO

def mns(ref1, ref2, symbolmap):
    ref1, ref2 = _(ref1, symbolmap), _(ref2, symbolmap)
    if type(ref1) == type(ref2) and type(ref2) == type(Array([])):
        return Array([element for element in ref1.elements if element not in ref2.elements])
    elif type(ref2) == type(Array([])):
        return Array([ref1 - element for element in ref2.elements])
    elif type(ref1) == type(Array([])):
        return Array([ref2 - element for element in ref1.elements])
    return ref1 - ref2 # TODO

def mod(ref1, ref2, symbolmap):
    ref1, ref2 = _(ref1, symbolmap), _(ref2, symbolmap)
    return ref1 % ref2 # TODO

def mul(ref1, ref2, symbolmap):
    ref1, ref2 = _(ref1, symbolmap), _(ref2, symbolmap)
    return ref1 * ref2 # TODO

def div(ref1, ref2, symbolmap):
    ref1, ref2 = _(ref1, symbolmap), _(ref2, symbolmap)
    return ref1 / ref2 # TODO

def exp(ref1, ref2, symbolmap):
    ref1, ref2 = _(ref1, symbolmap), _(ref2, symbolmap)
    return ref1 ** ref2 # TODO

def inv(ref, symbolmap):
    ref = _(ref)
    return not ref # TODO

def inc(ref, symbolmap):
    return asn(ref, _(ref, symbolmap) + 1, symbolmap)

def dec(ref, symbolmap):
    return asn(ref, _(ref, symbolmap) - 1, symbolmap)

def postinc(ref, symbolmap):
    pre = _(ref, symbolmap)
    asn(ref, _(ref) + 1, symbolmap)
    return pre

def postdec(ref, symbolmap):
    pre = _(ref, symbolmap)
    asn(ref, _(ref) - 1, symbolmap)
    return pre

def factorial(ref, symbolmap):
    ref = _(ref, symbolmap)
    if type(ref) == type(sympy.Integer(2)):
        return sympy.factorial(ref)
    else:
        raise RuntimeError("Factorial on non-int object of type %s" % str(type(ref)))

class actualNone():
    def __init__(self):
        pass

class Return():
    def __init__(self, value):
        self.value = value

class Interpreter():
    def __init__(self, args = None, func_args = None, tree = None, symbolmap = None, directory = ""):
        self.tree = tree or ParseTree()
        self.func_args = func_args
        self.args = args or []
        self.symbolmap = symbolmap or {}
        self.directory = directory
    def evaluate(self, node, preserve_ref = False, func_args = None):
        log("EVAL: %s" % str(node))
        log("FUNC: %s" % str(func_args))
        if type(node) == type(ParseTree()) and not node.type:
            array = [self.evaluate(child, preserve_ref, func_args) for child in node.children]
            return array[0] if len(array) == 1 else array
        elif type(node) == type(IdentifierContainer("")):
            return _(node, self.symbolmap)
        elif node.type == "operator":
            if len(node.children) == 2:
                evals = [self.evaluate(child, node.content in assignment_operators, func_args) for child in node.children]
                if node.content == "@":
                    return get(evals[0], evals[1], self.symbolmap, True)
                else:
                    return operators[node.content](evals[0], evals[1], self.symbolmap)
            elif len(node.children) == 1:
                return prefix_variants[node.content](self.evaluate(node.children[0], node.content in assignment_operators, func_args), self.symbolmap)
        elif node.type == "item":
            if node.content == "list":
                return Array([_(self.evaluate(child, preserve_ref, func_args), self.symbolmap) for child in node.children])
            elif node.content == "bracket":
                postops = []
                keep_ref = False
                for child in node.children[::-1]:
                    if child.type == "operator" and child.content in postfix and not child.children:
                        postops.insert(0, child.content)
                        keep_ref |= child.content in assignment_operators
                        node.children = node.children[:-1]
                if node.children:
                    if len(node.children) == 1:
                        result = self.evaluate(node.children[0], keep_ref, func_args)
                        if type(result) == type(actualNone()):
                            result = ()
                    else:
                        result = tuple([x for x in [self.evaluate(child, keep_ref, func_args) for child in node.children] if type(x) != type(actualNone())])
                    for postop in postops:
                        result = postfix_variants[postop](result)
                    return result
                else:
                    return ()
            elif node.content == "function":
                def function(*arguments):
                    syms = {}
                    for key in self.symbolmap:
                        syms[key] = self.symbolmap[key]
                    interpreter = Interpreter(self.args, arguments, None, syms)
                    for child in node.children:
                        value = interpreter.evaluate(child)
                        if type(value) == type(Return("")):
                            return value.value
                return Function(function)
            else:
                keep_ref = any(child.content in assignment_operators for child in node.children)
                if not hasattr(node.content, "type"):
                    log("Don't know what <item " + str(node.content) + "> is doing here.")
                elif node.content.type == "identifier":
                    result = IdentifierContainer(str(node.content.content))
                    if not (keep_ref or preserve_ref):
                        result = _(result, self.symbolmap)
                elif node.content.type == "sysarg":
                    if len(self.args) > node.content.content:
                        result = self.args[node.content.content]
                    else:
                        raise RuntimeError("Index %d out of range for system arguments %s" % (node.content.content, str(self.args)))
                elif node.content.type == "funcarg":
                    if self.func_args == None and func_args == None:
                        raise RuntimeError("Cannot get function arguments outside of a function")
                    elif node.content.content == 0:
                        return func_args or self.func_args
                    elif func_args and len(func_args) > node.content.content - 1:
                        result = func_args[node.content.content - 1]
                    elif self.func_args and len(self.func_args) > node.content.content - 1:
                        result = self.func_args[node.content.content - 1]
                    else:
                        raise RuntimeError("Index %d out of range for function arguments %s and %s" % (node.content.content, str(self.func_args), str(func_args)))
                else:
                    result = node.content.content
                for child in node.children:
                    result = postfix_variants[child.content](result, self.symbolmap)
                return result
        elif node.type in ["if", "elif"]:
            if len(node.children) < 2:
                raise RuntimeError("IF statement should be in the format `if <condition> then { <code> } [ elif <condition> then { <code> }...] [ else { <code> } ]`")
            else:
                if self.evaluate(node.children[0], False, func_args):
                    for child in node.children[1].children:
                        self.evaluate(child, False, func_args)
                elif node.children[2:]:
                    self.evaluate(node.children[2], False, func_args)
        elif node.type == "while":
            if len(node.children) != 2:
                raise RuntimeError("WHILE statement should be in the format `while <condition> do { <code> }`")
            else:
                while self.evaluate(node.children[0], False, func_args):
                    for child in node.children[1].children:
                        self.evaluate(child, False, func_args)
        elif node.type == "foreach":
            if len(node.children) != 2:
                raise RuntimeError("FOREACH statement should be in the format `foreach <iterable> do { <code> }`")
            else:
                for x in self.evaluate(node.children[0], False, func_args):
                    for child in node.children[1].children:
                        self.evaluate(child, False, func_args = [x])
        elif node.type == "else":
            for child in node.children:
                self.evaluate(child, False, func_args)
        elif node.type == "return":
            if node.children:
                return Return(self.evaluate(node.children[0], False, func_args))
            else:
                return Return(None)
        elif node.type == "import":
            if len(node.children) == 1:
                packages = self.evaluate(node.children[0], True, func_args)
                if hasattr(packages, "__iter__"):
                    for package in packages:
                        self.symbolmap[package.name] = self.Import(package.name + ".pos")
                else:
                    self.symbolmap[packages.name] = self.Import(packages.name + ".pos")
            else:
                raise RuntimeError("IMPORT statement should be in the format `import file1[, file2, ...]`")
        elif node.type == "include":
            if len(node.children) == 1:
                child = node.children[0]
                packages = self.evaluate(node.children[0], True, func_args)
                if hasattr(packages, "__iter__"):
                    for package in packages:
                        syms = self.Import(package.name + ".pos")
                        for key in syms:
                            self.symbolmap[key] = syms[key]
                else:
                    syms = self.Import(packages.name + ".pos")
                    for key in syms:
                        self.symbolmap[key] = syms[key]
            else:
                raise RuntimeError("INCLUDE statement should be in the format `include file1[, file2, ...]`")
        elif node.type == "pyimport":
            if len(node.children) == 1:
                packages = self.evaluate(node.children[0], True, func_args)
                if hasattr(packages, "__iter__"):
                    for package in packages:
                        self.symbolmap[package.name] = self.PythonImport(self.directory, package.name)
                else:
                    self.symbolmap[packages.name] = self.PythonImport(self.directory, packages.name)
            else:
                raise RuntimeError("PYIMPORT statement should be in the format `pyimport file1[, file2, ...]`")
        elif node.type == "pyinclude":
            if len(node.children) == 1:
                child = node.children[0]
                packages = self.evaluate(node.children[0], True, func_args)
                if hasattr(packages, "__iter__"):
                    for package in packages:
                        syms = self.PythonImport(self.directory, package.name)
                        for key in syms:
                            self.symbolmap[key] = syms[key]
                else:
                    syms = self.PythonImport(self.directory, packages.name)
                    for key in syms:
                        self.symbolmap[key] = syms[key]
            else:
                raise RuntimeError("PYINCLUDE statement should be in the format `pyinclude file1[, file2, ...]`")
        elif node.type == "null":
            return actualNone()
    def Import(self, directory, package, use_new_interpreter = True):
        interpreter = getDefaultInterpreter() if use_new_interpreter else self
        interpreter.args = self.args
        with open(directory + "/" + package, "r") as f:
            code = f.read()
            tokenizer = Tokenizer(code)
            parser = Parser([])
            while tokenizer.hasNext():
                next = tokenizer.next()
                if next:
                    parser.addToken(next)
            tree = parser.fill()
            for subtree in tree.children:
                try:
                    interpreter.evaluate(subtree, False)
                except:
                    print(tree)
                    raise
        return interpreter.symbolmap
    def PythonImport(self, directory, package):
        imported = __import__(package)
        syms = {}
        for attr in dir(imported):
            obj = getattr(imported, attr)
            if type(obj) == type(lambda:0) or type(obj) == type(print):
                syms[attr] = Function(obj)
            elif type(obj) == type(0) or type(obj) == type(0.1):
                syms[attr] = sympy.Rational(obj)
            else:
                syms[attr] = obj
        return syms

prefix_variants = {
    "+": lambda x, symbolmap: _(x, symbolmap),
    "-": lambda x, symbolmap: mns(sympy.Integer(0), x, symbolmap),
    "++": inc,
    "--": dec,
    "!": inv,
    "#": lambda x, symbolmap: Interpreter(args = None, func_args = None, tree = None, symbolmap = symbolmap).evaluate(Parser(Tokenizer(x).tokenize()).fill()),
}

assignment_operators = ["=", "+=", "-=", "*=", "**=", "%=", "++", "--", "."]

operators = {
    "=": asn,
    "+=": addasn,
    "-=": mnsasn,
    "*=": mulasn,
    "**=": expasn,
    "/=": divasn,
    "%=": modasn,
    "==": equ,
    "!=": neq,
    ">": gt,
    "<": lt,
    ">=": geq,
    "<=": leq,
    "@": get,
    "+": add,
    "-": mns,
    "%": mod,
    "*": mul,
    "/": div,
    "**": exp,
    ".": subref,
}

postfix_variants = {
    "++": postinc,
    "--": postdec,
    "!": factorial,
    "@@": getdefault,
}

class Reference():
    def __init__(self, value, assign):
        self.value = value
        self.assign = assign

class Array():
    def __init__(self, elements):
        self.elements = [element for element in elements if type(element) != type(actualNone())]
    def get(self, index = 0):
        def assign(x):
            self.elements[index] = x
        return Reference(self.elements[index], assign)
    def __str__(self):
        return str(self.elements)
    def __repr__(self):
        return str(self)
    def __iter__(self):
        return self.elements.__iter__()
    def __len__(self):
        return self.elements.__len__()

class Function():
    def __init__(self, function):
        self.get = function

class IdentifierContainer():
    def __init__(self, name):
        self.name = name
    def __str__(self):
        return self.name
    def __repr__(self):
        return self.name

import time

if __name__ == "__main__":
    while True:
        try:
            code = sys.argv[1] if sys.argv[1:] else input("Enter code to be interpreted >>> ")

            if sys.argv[1:]: sys.argv = sys.argv[1:]

            tokenizer = Tokenizer(code)

            parser = Parser([])

            while tokenizer.hasNext():
                next = tokenizer.next()
                if next:
                    parser.addToken(next)

            tree = parser.fill()

            interpreter = getDefaultInterpreter()

            print([_(value, interpreter.symbolmap) for value in map(interpreter.evaluate, tree.children)])

            tree.remove_all()
        except Exception as e:
            err("ERROR: %s" % str(e))
