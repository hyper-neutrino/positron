import time
import interpreter

print = print
input = input
exec = exec
eval = eval
sleep = time.sleep
len = len
stringify = str
str = lambda x: stringify(x)
ran = range
range = lambda *a: list(ran(*map(int, a)))
typeof = lambda x: type(x)
__pyimport__ = lambda x: interpreter.getDefaultInterpreter().PythonImport(x)
def safe(func, handler = None):
    try:
        return func.get()
    except Exception as e:
        if handler:
            handler.get(e)
