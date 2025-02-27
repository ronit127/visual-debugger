import trace
import io
import sys
import re

# take in some code, convert into a form python understands, and executes it
def process_code(code):
    print("executing code")
    exec(code) # TODO: figure out how to collect errors and print them without stopping our program
    print("check")


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