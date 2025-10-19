import trace
import io
import sys
import re

code_lines = []

def processCode(code_input):
    global code
    code = code_input

    output_buffer = io.StringIO()
    sys.stdout = output_buffer

    tracer = trace.Trace(trace=True, count=False)
    tracer.run(code)


    sys.stdout = sys.__stdout__
   
    s = output_buffer.getvalue()
    # print("This is s:" + s)
    global code_lines
    code_lines = code.splitlines()
  
    return s

def getLine(n):
    if len(code_lines) > 0:
        return code_lines[n-1]
    else: return None

def getFunctionLine(func):  # returns line number 2-indexed  (i.e. first line is a 2) if function declaration in the code, -1 otherwise.
    for i in range(0, len(code_lines)):
        line = code_lines[i]
        if line.startswith("def " + func):
            return i + 1
    return -1


def parseTrace(trace_str):
    trace = []
    start = trace_str.find("--- modulename: test2, funcname: main")
    trace_str = trace_str[start:]
    pattern = r"(?:--- modulename: test2, funcname: (\w+)|<string>\((\d+)\))"

    matches = re.finditer(pattern, trace_str)

    for match in matches:
        funcname = match.group(1)  # Captures the funcname
        linenumber = match.group(2)  # Captures the linenumber
        if funcname:
            trace.append(getFunctionLine(funcname))
        if linenumber:
            trace.append(int(linenumber))
        
    return trace

def execCode(code):

    s = processCode(code)
    trace = parseTrace(s)
    print(trace)
    print(code_lines)

code = """
def test_function():
    x = 10
    y = 20
    for i in range(0, 5):
        x += 10
    helper()
    return x + y

    def helper():
        pass
    
def main():
       print("hello")
       test_function()
"""

print(execCode(code))

import ast

c = """
l = [1, 2, 3, 4]
l.append(1)
l.pop()
"""



def list_parse(code: str):
    tree = ast.parse(code)
    list_vars = set()

# walking throuhg ast nodes
# need class for bc ast works with classes that extend NodeVisitor
    class Functions(ast.NodeVisitor):
        #whenever x= is found
        def visit_Assign(self, node):
            # checks if it is a list assignment
            if isinstance(node.value, ast.List):
                # if a list adds the variable names
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        list_vars.add(target.id)
                        for elt in node.value.elts:
                        # call the visualization add
                            print("adding existing element") # call the visualization add
            #self.generic_visit(node) # keep going through the rest of the tree under this node so nothing else gets missed
           


        def visit_Call(self, node):
            # check if method call on variable
            if isinstance(node.func, ast.Attribute) and isinstance(node.func.value, ast.Name):
                var_name = node.func.value.id
                method_name = node.func.attr
                if var_name in list_vars:
                    if method_name == 'append'or method_name == 'push':
                        print("adding a node") # call tje visualization add
                    elif method_name == 'pop':
                        print("deleting a node") # call the visualization delete
            #self.generic_visit(node)
    #visit_assign and visit_call get called automatically by the NodeVisitor
    Functions().visit(tree)


list_parse(c)




