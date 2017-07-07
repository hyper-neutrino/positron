from tokenizer import *
from parser import *
from interpreter import *
import os

if __name__ == "__main__":
    if sys.argv[1:]:
        filename = sys.argv[1]
        with open(filename, "r") as f:
            code = f.read()
            tokenizer = Tokenizer(code)
            parser = Parser([])
            while tokenizer.hasNext():
                next = tokenizer.next()
                if next:
                    parser.addToken(next)
            tree = parser.fill()
            evaluator = getDefaultInterpreter()
            for subtree in tree.children:
                try:
                    evaluator.evaluate(subtree)
                except:
                    print(tree)
                    raise
