from tokenizer import *
from parser import *
from interpreter import *

if __name__ == '__main__':
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
            imports = evaluator.Import("core.pos")
            for key in imports:
                evaluator.symbolmap[key] = imports[key]
            imports = evaluator.PythonImport("core")
            for key in imports:
                evaluator.symbolmap[key] = imports[key]
            for subtree in tree.children:
                try:
                    evaluator.evaluate(subtree)
                except:
                    print(tree)
                    raise
