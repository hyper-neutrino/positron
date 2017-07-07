from logger import *
import re, sympy, sys

def rfunc(pattern, sub, function = None):
    return lambda string: (function or (lambda x: x))(re.sub(pattern, sub, string))

def string_eval(quote):
    return lambda string: eval(quote + string + quote)

class TokenType():
    def __init__(self, name, functions = None):
        self.name = name
        self.functions = functions or []
    def __str__(self):
        return 'TokenType@%s' % self.name
    def __repr__(self):
        return str(self)

patterns = [
    ("//.*$", TokenType("")),
    ("\"([^\"]|\\.)*\"", TokenType("string", [
        rfunc("\"(([^\"]|\\.)*)\"", "\\1"),
        rfunc("^(.*)$", "\\1", string_eval("\""))
    ])),
    ("\'([^\']|\\.)*\'", TokenType("string", [
        rfunc("\'(([^\']|\\.)*)\'", "\\1"),
        rfunc("^(.*)$", "\\1", string_eval("\'"))
    ])),
    ("(\\d+(\\.\\d*)?|\\d*\\.\\d+)", TokenType("number", [
        sympy.Rational
    ])),
    ("\\$\\$\\d+", TokenType("sysarg", [
        rfunc("\\$\\$(\\d+)", "\\1", int)
    ])),
    ("\\$\\d+", TokenType("funcarg", [
        rfunc("\\$(\\d+)", "\\1", int)
    ])),
    ("(return|if|elif|while|import)", TokenType("keyword")),
    ("(\\#|>(=|>=?)?|<(=|<=?)?|-[=-]?|\\+[=\\+]?|==?|\\*(=|\\*=?)?|!=?|@@?|%=?|/=?|\\.)", TokenType("operator")),
    ("\\[", TokenType("listhead")),
    ("\\]", TokenType("listtail")),
    ("\\(", TokenType("brakhead")),
    ("\\)", TokenType("braktail")),
    ("function\\s*\\{", TokenType("funchead")),
    ("then\\s*\\{", TokenType("thenhead")),
    ("else\\s*\\{", TokenType("elsehead")),
    ("do\\s*\\{", TokenType("dohead")),
    ("\\}", TokenType("bloctail")),
    (",", TokenType("comma")),
    (";", TokenType("statement")),
    ("[A-Za-z_][A-Za-z_0-9]*", TokenType("identifier")),
]

class Token():
    def __init__(self, type, content):
        self.type = type
        self.content = content
    def __str__(self):
        return "<%s:%s[%s]>" % (self.type, str(self.content), str(type(self.content)))
    def __repr__(self):
        return str(self)

class Tokenizer():
    def __init__(self, code):
        self.code = code.replace("\\\n", "")
        self.index = 0
    def hasNext(self):
        return self.index < len(self.code)
    def tokenize(self):
        tokens = []
        while self.hasNext():
            next = self.next()
            if next:
                tokens.append(next)
        return tokens
    def next(self):
        code = self.code[self.index:]
        log('-' * 24 + '\n' + code)
        if code.startswith("/*"):
            while not self.code[self.index:].startswith("*/"):
                self.index += 1
            self.index += 2
            return None
        elif code.startswith("\"\"\"") or code.startswith("\'\'\'"):
            close = code[:3]
            self.index += 3
            code = self.code[self.index:]
            string = ""
            while not code.startswith(close):
                if code[0] == "\\":
                    self.index += 1
                    string += eval("\"\\%s\"" % code[1])
                else:
                    string += code[0]
                self.index += 1
                code = self.code[self.index:]
            self.index += 3
            return Token("string", string)
        for pattern in patterns:
            match = re.match(pattern[0], code)
            if match:
                if pattern[1].name:
                    content = match.group(0)
                    for function in pattern[1].functions:
                        content = function(content)
                    self.index += match.end(0)
                    return Token(pattern[1].name, content)
                else:
                    self.index += match.end(0)
                    return self.next()
        self.index += 1

if __name__ == "__main__":
    while True:
        try:
            code = sys.argv[1] if sys.argv[1:] else input("Enter code to be tokenized >>> ")

            if sys.argv[1:]: sys.argv = sys.argv[1:]

            tokenizer = Tokenizer(code)

            while tokenizer.hasNext():
                next = tokenizer.next()
                if next:
                    print(next)
        except Exception as e:
            err("ERROR: %s" % str(e))
