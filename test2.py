import trace
import io
import sys
import re

# take in some code, and executes it
def execute_code(code):
    print("executing code...")
    status = "" # TODO: change status according to either the output or the run-time / syntax errors of the code (should use stdout redirect or similar), statsus is the error i am printing out

    try:
        compiled_code = compile(code, "<string>", "exec")  # Check for syntax errors
        exec(compiled_code)  # Execute if no syntax errors
    except SyntaxError as e:
        #status = 0
        status = e
        print(f"indent error happened: {e}")
    except IndentationError as e:
        status = e
        print(f"error happened: {e}")
    except NameError as e:
        status = e
        print(f"error happened: {e}")
    except Exception as e:  # Catch other runtime errors
        status = "No syntax errors"
        pass
        print("still executing")

    #exec(code) # TODO: figure out how to collect errors and print them without stopping our program
    # try:
    #     exec(code)
    # except Exception as e:
    #     if isinstance(e, SyntaxError):
    #     #     status = "syntax error"
    #     #     print(status)
    #         print(f"Error happened: {e}")
        # else:
        #     pass
    # except Exception:
    #     pass

    #TODO: Come up with ways to safely execute the code (prevent malicious code), forking, loops that don't end
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
    z = [1, 2, 3]
    for i in range(0, 5):
        y += z[i]
    return x
    
print(test_function())
"""

print(execute_code(code))