import trace
import io
import sys
import re

# take in some code, and executes it
def execute_code(code):
    print("executing code...")
    exec(code) # TODO: figure out how to collect errors and print them without stopping our program
    
    status = "" # TODO: change status according to either the output or the run-time / syntax errors of the code (should use stdout redirect or similar)

    #TODO: Come up with ways to safely execute the code (prevent malicious code)
    return status

# take in some code, give a list of lines in the order they are run when executed.
# this allows us to know the order of lines we need to highlight and more importantly, process and visualize 
def trace_code(code):
    #TODO: use the trace function to go through the input code (perhaps the Trace() and run() functions among others)

    #TODO: return a list of tuples in the form (n, x) where n is the line number and x is the corresponidng line of code (String)
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