import trace
import io
import sys
import re

# take in some code, convert into a form python understands, and executes it
def execute_code(code):
    print("executing code")
    exec(code) # TODO: figure out how to collect errors and print them without stopping our program
    status = 0
    
    return status, string

# take in some code, give a list of lines that are run
def trace_code(code):
    #TODO: use the trace function to go through the input code
    pass

code = """
def test_function():
    x = 10
    y = 20
    for i in range(0, 5):
    x += 10
    return x+y
    
print(test_function())
"""

process_code(code)