"""
tracer.py - Generate execution traces for debugger

This module runs Python code and captures the execution trace.
Handles syntax errors and runtime errors gracefully.
"""

import sys
import io
import trace as trace_module
import re


def generate_trace(code):
    """
    Execute code and generate execution trace.
    Handles both syntax errors and runtime errors gracefully.
    
    Args:
        code: Python code string to execute
    
    Returns:
        tuple: (trace_list, output, error)
            - trace_list: List of line numbers executed [1, 2, 3, ...] (empty if error before execution)
            - output: String output from code execution
            - error: Error message if any, None otherwise
    """
    # Save original stdout and stderr
    old_stdout = sys.stdout
    old_stderr = sys.stderr
    
    # Capture stdout for BOTH program output AND trace output
    # (trace module writes to stdout, not stderr!)
    combined_buffer = io.StringIO()
    
    # Separate buffer for actual program output
    output_buffer = io.StringIO()
    
    error = None
    trace_list = []
    
    try:
        # First, try to compile the code to catch syntax errors
        compiled_code = compile(code, "<string>", "exec")
        
        # Create tracer that writes to a file-like object
        tracer = trace_module.Trace(trace=True, count=False)
        
        # Redirect stdout to capture BOTH trace and print statements
        sys.stdout = combined_buffer
        sys.stderr = combined_buffer  # Capture stderr too just in case
        
        try:
            # Run the code with tracing
            tracer.run(compiled_code)
        except Exception as runtime_error:
            # Runtime error occurred during execution
            error = f"Runtime Error: {type(runtime_error).__name__}: {str(runtime_error)}"
        
    except SyntaxError as syntax_error:
        # Syntax error - code won't compile
        error = f"Syntax Error: {str(syntax_error)}"
        
    except Exception as e:
        # Other compilation errors
        error = f"Compilation Error: {type(e).__name__}: {str(e)}"
        
    finally:
        # Always restore original streams
        sys.stdout = old_stdout
        sys.stderr = old_stderr
    
    # Get combined output
    combined_output = combined_buffer.getvalue()
    
    # Separate trace lines from program output
    trace_list, program_output = parse_trace_and_output(combined_output)
    
    return trace_list, program_output, error


def parse_trace_and_output(combined_str):
    """
    Parse combined output to separate trace lines from program output.
    
    Args:
        combined_str: Combined trace and program output
    
    Returns:
        tuple: (trace_list, program_output)
    """
    trace = []
    output_lines = []
    
    lines = combined_str.split('\n')
    
    for line in lines:
        # Check if this is a trace line
        if '<string>(' in line:
            # Extract line number
            match = re.search(r'<string>\((\d+)\)', line)
            if match:
                trace.append(int(match.group(1)))
        elif line.startswith(' --- modulename:') or line.startswith('---'):
            # Skip trace metadata lines
            continue
        else:
            # This is program output
            if line or output_lines:  # Don't add leading empty lines
                output_lines.append(line)
    
    # Join output lines and clean up trailing newlines
    program_output = '\n'.join(output_lines).rstrip('\n')
    if program_output:
        program_output += '\n'
    
    return trace, program_output


def parse_trace_output(trace_str):
    """
    Parse trace module output to extract line numbers.
    
    Args:
        trace_str: Raw trace output
    
    Returns:
        List of line numbers in execution order
    """
    trace = []
    pattern = r"<string>\((\d+)\)"
    
    matches = re.finditer(pattern, trace_str)
    
    for match in matches:
        line_num = match.group(1)
        if line_num:
            trace.append(int(line_num))
    
    return trace


def generate_trace_from_file(filepath):
    """
    Read code from file and generate trace.
    
    Args:
        filepath: Path to Python file
    
    Returns:
        tuple: (trace_list, output, error, code)
            - trace_list: List of line numbers
            - output: Execution output
            - error: Error message if any
            - code: The code that was read from file
    """
    try:
        with open(filepath, 'r') as f:
            code = f.read()
        
        trace_list, output, error = generate_trace(code)
        return trace_list, output, error, code
        
    except FileNotFoundError:
        return [], "", f"File not found: {filepath}", ""
    except Exception as e:
        return [], "", f"Error reading file: {str(e)}", ""


# Test function
if __name__ == "__main__":
    print("=" * 60)
    print("TRACE MODULE TEST")
    print("=" * 60)
    
    # Test 1: Valid code
    print("\n--- Test 1: Valid Code ---")
    test_code = """x = 1
y = 2
z = x + y
print(z)"""
    
    trace_list, output, error = generate_trace(test_code)
    print(f"Trace: {trace_list}")
    print(f"Trace length: {len(trace_list)}")
    print(f"Output: {repr(output)}")
    print(f"Error: {error}")
    
    # Test 2: Syntax error
    print("\n--- Test 2: Syntax Error ---")
    bad_syntax = """x = 1
y = 2
z = x +"""  # Missing operand
    
    trace_list, output, error = generate_trace(bad_syntax)
    print(f"Trace: {trace_list}")
    print(f"Output: {repr(output)}")
    print(f"Error: {error}")
    
    # Test 3: Runtime error
    print("\n--- Test 3: Runtime Error ---")
    runtime_err = """x = 1
y = 0
z = x / y"""  # Division by zero
    
    trace_list, output, error = generate_trace(runtime_err)
    print(f"Trace: {trace_list}")
    print(f"Output: {repr(output)}")
    print(f"Error: {error}")
    
    # Test 4: Function call
    print("\n--- Test 4: Function Call ---")
    func_code = """def add(a, b):
    return a + b

result = add(3, 4)
print(result)"""
    
    trace_list, output, error = generate_trace(func_code)
    print(f"Trace: {trace_list}")
    print(f"Trace length: {len(trace_list)}")
    print(f"Output: {repr(output)}")
    print(f"Error: {error}")