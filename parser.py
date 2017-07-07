from tokenizer import *
from logger import *
import sys

operator_precedence = { # TODO
    "=": 0,
    "+=": 0,
    "-=": 0,
    "*=": 0,
    "**=": 0,
    "/=": 0,
    "%=": 0,
    "==": 1,
    "!=": 1,
    ">": 1,
    "<": 1,
    ">=": 1,
    "<=": 1,
    "+": 3,
    "-": 3,
    "%": 4,
    "*": 5,
    "/": 5,
    "**": 6,
    "!": 7,
    "#": 8,
    "++": 9,
    "--": 9,
    "@": 10,
    "@@": 11,
    ".": 12
}

right_associative = [0, 10]

prefix = ["!", "++", "--", "+", "-", "*", "#"]
infix = ["=", "+=", "-=", "*=", "**=", "/=", "%=", "==", "!=", ">", "<", ">=", "<=", "@", "+", "-", "%", "*", "/", "**", "."]
postfix = ["++", "--", "!", "@@"]

id = -1
def getID():
    global id
    id += 1
    return id

def keepBranch(node, current):
    nodeprec = operator_precedence[node]
    currprec = operator_precedence[current]
    return nodeprec > currprec or nodeprec == currprec and nodeprec not in right_associative

class ParseTree():
    def __init__(self, type = None, content = None, root = None, children = None, flag = False, id = -1):
        self.type = type
        self.content = content
        self.root = root
        self.children = children or []
        self.target = self
        self.id = (id + 1 or getID() + 1) - 1
        self.flag = flag
    def add_child(self, child):
        self.children.append(child)
        child.root = self
    def remove_child(self, child):
        try:
            self.children.remove(child)
            child.root = None
        except:
            pass # Safe if the parameter wasn't a child of this tree anyway
    def pushOperator(self, operator):
        child = ParseTree(type = "operator", content = operator)
        if self.target.type == "operator":
            if operator in postfix and operator not in prefix + infix:
                if self.target.children:
                    self.target.children[-1].add_child(child)
                elif self.target.content in postfix:
                    self.target.add_child(child)
                    self.target = child
                else:
                    raise RuntimeError("Postfix operator directly after non-postfix operator")
            if not self.target.flag and operator in infix and self.target.content in infix and len(self.target.children) == 2:
                if keepBranch(self.target.content, operator):
                    root = self.target.root
                    root.remove_child(self.target)
                    child.add_child(self.target)
                    root.add_child(child)
                    self.target = child
                else:
                    branch = self.target.children[-1]
                    self.target.remove_child(branch)
                    child.add_child(branch)
                    self.target.add_child(child)
                    self.target = child
            elif self.target.content in postfix and operator not in postfix:
                self.target = self.target.root
                self.pushOperator(operator)
            elif not self.target.flag and operator in prefix:
                self.target.add_child(child)
                self.target = child
            elif self.target.flag and operator in infix:
                root = self.target.root
                root.remove_child(self.target)
                child.add_child(self.target)
                root.add_child(child)
                self.target = child
            else:
                raise RuntimeError("No item preceding non-prefix operator")
        elif self.target == self:
            if operator in prefix:
                self.target.add_child(child)
                self.target = child
            else:
                raise RuntimeError("No item preceding non-prefix operator")
        elif self.target.type == "item":
            if operator in postfix:
                self.target.add_child(child)
                self.target = child
            elif (self.target.content in ["list", "bracket"] or self.target.root == self) and (operator in postfix and not self.target.root.flag or operator in prefix and not self.target.flag and self.target.root != self):
                self.target.add_child(child)
                self.target = child
            elif self.target.root.type == "operator":
                if keepBranch(self.target.root.content, operator):
                    root = self.target.root
                    rootroot = self.target.root.root
                    rootroot.remove_child(root)
                    child.add_child(root)
                    rootroot.add_child(child)
                    self.target = child
                else:
                    root = self.target.root
                    root.remove_child(self.target)
                    child.add_child(self.target)
                    root.add_child(child)
                    self.target = child
            else:
                root = self.target.root
                root.remove_child(self.target)
                child.add_child(self.target)
                root.add_child(child)
                self.target = child
        elif self.target.type == "return":
            self.target.add_child(child)
            self.target = child
        elif self.target.type in ["if", "elif", "while"]:
            self.target.add_child(child)
    def pushItem(self, item):
        child = ParseTree(type = "item", content = item)
        if item.type == "comma":
            if self.target.type == "item":
                if self.target.root and self.target.root.content == "bracket":
                    self.target.root.flag = True
                    self.target = self.target.root
                else:
                    root = self.target.root
                    root.remove_child(self.target)
                    child = ParseTree(type = "bracket", content = None, root = root, children = [self.target], flag = True, id = -1)
                    root.add_child(child)
                    self.target = child
        elif self.target == self:
            self.target.add_child(child)
            self.target = child
        elif self.target.type == "item":
            raise RuntimeError("Cannot push item onto another item on AST")
        elif self.target.type == "operator":
            if self.target.content in prefix and not self.target.children:
                self.target.add_child(child)
                self.target.flag = True
                self.target = self.target.root
            elif self.target.content in infix and len(self.target.children) < 2:
                self.target.add_child(child)
                self.target = child
            elif self.target.content in postfix:
                raise RuntimeError("Cannot push item onto a postfix-only operator")
            else:
                self.target = self.target.root
                self.pushItem(item)
        elif self.target.type in ["return", "if", "elif", "while", "import"]:
            self.target.add_child(child)
            self.target = child
        elif self.target.type == "bracket" and self.target.flag:
            self.target.flag = False
            self.target.add_child(child)
    def getHead(self):
        return self.root.getHead() if self.root else self
    def remove_all(self):
        for child in self.children:
            if child != self:
                child.remove_all()
            self.remove_child(child)
    def __str__(self, target = None, recurse = 0):
        target = target or self.target
        repr = "%s:[Node content = %s type = %s]:%d>%s" % (self.type, str(self.content), type(self.content), self.id, str(self.root.id if self.root else "x")) if self.type else "HEAD:%d%s" % (self.id, "$" if self == target else "")
        # repr = (str(self.content.content) if type(self.content) == type(Token(None, None)) else str(self.content)) if self.type else "HEAD"
        for child in self.children:
            try:
                if recurse > 10:
                    raise RuntimeError("force_overflow")
                lines = child.__str__(target, recurse + 1).split("\n")
                repr += "\n\\----%s%s%s" % (lines[0], "$" if child == target else "", "!" if child.flag else "")
                for line in lines[1:]:
                    repr += "\n|    %s" % line
            except Exception as e:
                repr += "\n    | " + str(e)
        return repr # if recurse or repr.count("$") == 1 else "This is going to get ugly when you try to evaluate it..."
    def __repr(self):
        return str(self)

class Parser():
    def __init__(self, tokens = None):
        self.tokens = tokens or []
        log("Created parser with tokens %s" % str(self.tokens))
    def fill(self):
        tree = ParseTree(None, None, None, [], False, -1)
        index = 0
        balanceable = {
            "listhead": ("listtail", "list"),
            "brakhead": ("braktail", "bracket"),
            "funchead": ("bloctail", "function"),
            "thenhead": ("bloctail", "then", ["if", "elif"]),
            "elsehead": ("bloctail", "else", ["if", "elif"]),
            "dohead": ("bloctail", "do", ["while"])
        }
        ends = ["listtail", "braktail", "bloctail"]
        typed = ["else"]
        while index < len(self.tokens):
            token = self.tokens[index]
            log("------------\nPushing %s onto target:\n%s\n\n" % (str(token), str(tree.target)))
            if token.type == "operator":
                tree.pushOperator(token.content)
            elif token.type in balanceable:
                index += 1
                inner_tokens_list = [[]]
                brackets = 1
                while brackets:
                    if self.tokens[index].type in balanceable:
                        brackets += 1
                        if brackets:
                            inner_tokens_list[-1].append(self.tokens[index])
                    elif self.tokens[index].type in ends:
                        brackets -= 1
                        if brackets:
                            inner_tokens_list[-1].append(self.tokens[index])
                        elif self.tokens[index].type != balanceable[token.type][0]:
                            raise RuntimeError("Mismatched brackets")
                    elif self.tokens[index].type == "comma" and brackets == 1:
                        inner_tokens_list.append([])
                    else:
                        inner_tokens_list[-1].append(self.tokens[index])
                    index += 1
                log("Bracket closed with tokens: %s" % str(inner_tokens_list))
                if balanceable[token.type][2:]:
                    while tree.target.type not in balanceable[token.type][2]:
                        tree.target = tree.target.root
                if balanceable[token.type][1] in typed:
                    child = ParseTree(type = balanceable[token.type][1], content = None, root = None, children = [], flag = False, id = -1)
                else:
                    child = ParseTree(type = "item", content = balanceable[token.type][1], root = None, children = [], flag = False, id = -1)
                tree.target.add_child(child)
                tree.target = child
                for inner_tokens in inner_tokens_list:
                    if inner_tokens:
                        parser = Parser(inner_tokens)
                        subtree = parser.fill()
                        if token.type in ["funchead", "thenhead", "elsehead", "dohead"]:
                            for subchild in subtree.children:
                                child.add_child(subchild)
                        else:
                            if len(subtree.children) > 1:
                                raise RuntimeError("Subtree has %d children but should have at most 1" % len(subtree.children))
                            if subtree.children:
                                child.add_child(subtree.children[0])
                    else:
                        child.add_child(ParseTree(type = "null"))
                index -= 1
            elif self.tokens[index].type == "statement":
                tree.target = tree
            elif self.tokens[index].type == "keyword":
                requiredParent = {
                    "if": [],
                    "return": [],
                    "while": [],
                    "import": [],
                    "elif": ["if", "elif"],
                    "do": ["while"]
                }
                if self.tokens[index].content in ["if", "return", "elif", "while", "import"]:
                    while tree.target.type not in requiredParent[self.tokens[index].content] and requiredParent[self.tokens[index].content]:
                        tree.target = tree.target.root
                    child = ParseTree(self.tokens[index].content)
                    tree.target.add_child(child)
                    tree.target = child
            else:
                tree.pushItem(token)
            log(tree)
            index += 1
        return tree
    def addToken(self, token):
        self.tokens.append(token)

if __name__ == "__main__":
    while True:
        try:
            code = sys.argv[1] if sys.argv[1:] else input("Enter code to be parsed >>> ")

            if sys.argv[1:]: sys.argv = sys.argv[1:]

            tokenizer = Tokenizer(code)

            parser = Parser([])

            while tokenizer.hasNext():
                next = tokenizer.next()
                if next:
                    parser.addToken(next)

            tree = parser.fill()

            print(tree)

            tree.remove_all()
        except Exception as e:
            err("ERROR: %s" % str(e))
            raise
