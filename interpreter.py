from tokenizer import *
from parser import *
from logger import *

'''

datatypes
---------
string
number
list
regex

'''

def getDefaultInterpreter():
    return Interpreter(args = None, func_args = None, tree = None, symbolmap = {
        "print": Function(print),
        "input": Function(input),
        "type": Function(type),
        "exec": Function(exec),
        "eval": Function(eval),
        "sleep": Function(time.sleep),
        "str": Function(str),
        "len": Function(len),
    })

def _(ref, symbolmap):
    if hasattr(ref, "assign") and hasattr(ref, "value"):
        return ref.value
    elif type(ref) == type(IdentifierContainer("")):
        if str(ref) in symbolmap:
            return symbolmap[str(ref)]
        else:
            raise RuntimeError("Identifier %s is not defined" % str(ref))
    elif type(ref) == type(()):
        return tuple(map(_, ref))
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

def get(ref1, ref2, symbolmap):
    ref1, ref2 = _(ref1, symbolmap), _(ref2, symbolmap)
    if type(ref1) == type(""):
        return ref1[ref2]
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
    def __init__(self, args = None, func_args = None, tree = None, symbolmap = None):
        self.tree = tree or ParseTree()
        self.func_args = func_args
        self.args = args or []
        self.symbolmap = symbolmap or {}
    def evaluate(self, node, preserve_ref = False, do_things = True):
        log("EVAL: %s" % str(node))
        if type(node) == type(ParseTree()) and not node.type:
            array = [self.evaluate(child, preserve_ref) for child in node.children]
            return array[0] if len(array) == 1 else array
        elif type(node) == type(IdentifierContainer("")):
            return _(node, self.symbolmap)
        elif node.type == "operator":
            if len(node.children) == 2:
                evals = [self.evaluate(child, preserve_ref = node.content in assignment_operators) for child in node.children]
                if do_things or node.content != '@' or type(_(evals[1], self.symbolmap)) != type(Function(None)):
                    return operators[node.content](evals[0], evals[1], self.symbolmap)
            elif len(node.children) == 1:
                return prefix_variants[node.content](self.evaluate(node.children[0], preserve_ref = node.content in assignment_operators), self.symbolmap)
        elif node.type == "item":
            if node.content == "list":
                return Array([_(value, self.symbolmap) for value in map(self.evaluate, node.children)])
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
                        result = self.evaluate(node.children[0], preserve_ref = keep_ref)
                        if type(result) == type(actualNone()):
                            result = ()
                    else:
                        result = tuple([x for x in [self.evaluate(child, preserve_ref = keep_ref) for child in node.children] if type(x) != type(actualNone())])
                    for postop in postops:
                        if postop == "@@" and type(result) == type(Function(None)) and not do_things:
                            break
                        else:
                            result = postfix_variants[postop](result)
                    return result
                else:
                    return ()
            elif node.content == "function":
                def function(*arguments):
                    interpreter = Interpreter(self.args, arguments)
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
                    if self.func_args == None:
                        raise RuntimeError("Cannot get function arguments outside of a function")
                    elif len(self.func_args) > node.content.content:
                        result = self.func_args[node.content.content]
                    else:
                        raise RuntimeError("Index %d out of range for function arguments %s" % (node.content.content, str(self.func_args)))
                else:
                    result = node.content.content
                for child in node.children:
                    if child.content == "@@" and type(_(result, self.symbolmap)) == type(Function(None)) and not do_things:
                        break
                    else:
                        result = postfix_variants[child.content](result)
                return result
        elif node.type in ["if", "elif"]:
            if len(node.children) < 2:
                raise RuntimeError("IF statement should be in the format `if <condition> then { <code> } [ elif <condition> then { <code> }...] [ else { <code> } ]`")
            else:
                if self.evaluate(node.children[0]):
                    for child in node.children[1].children:
                        self.evaluate(child)
                elif node.children[2:]:
                    self.evaluate(node.children[2])
        elif node.type == "while":
            if len(node.children) != 2:
                raise RuntimeError("WHILE statement should be in the format `while <condition> do { <code> }`")
            else:
                while self.evaluate(node.children[0]):
                    for child in node.children[1].children:
                        self.evaluate(child)
        elif node.type == "else":
            for child in node.children:
                self.evaluate(child)
        elif node.type == "return":
            if node.children:
                return Return(self.evaluate(node.children[0]))
            else:
                return Return(None)
        elif node.type == "import":
            if len(node.children) == 1:
                packages = self.evaluate(node.children[0], True)
                if hasattr(packages, "__iter__"):
                    for package in packages:
                        self.symbolmap[package.name] = Interpreter.Import(package.name + ".txt")
                else:
                    self.symbolmap[packages.name] = Interpreter.Import(packages.name + ".txt")
            else:
                raise RuntimeError("IMPORT statement should be in the format `import file1[, file2, ...]`")
        elif node.type == "null":
            return actualNone()
    def Import(package):
        interpreter = getDefaultInterpreter()
        with open(package, "r") as f:
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
                    interpreter.evaluate(subtree, False, False)
                except:
                    print(tree)
                    raise
        return interpreter.symbolmap

prefix_variants = {
    "+": lambda x: x,
    "-": lambda x: mns(sympy.Integer(0), x),
    "++": inc,
    "--": dec,
    "!": inv,
    "#": lambda x: Interpreter().evaluate(Parser(Tokenizer(x).tokenize()).fill()),
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
        self.elements = elements
    def get(self, index = 0):
        def assign(x):
            self.elements[index] = x
        return Reference(self.elements[index], assign)
    def __str__(self):
        return str(self.elements)
    def __repr__(self):
        return str(self)

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
