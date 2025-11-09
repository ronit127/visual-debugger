"""
testing.py - Testing framework for debugger_core.py

This file provides a structured way to test the debugger with various code samples.
Easy to add new test cases and verify debugger behavior.

Usage:
    python testing.py
"""

from debugger import *
import os, sys
import pandas as pd


NUM_TESTS = 11

# ============================================
# TEST CODE SAMPLES
# ============================================

class TestCode:
    """
    Container for test code samples.
    Add new test cases by modifying debugger_test_cases folder
    """
    def __init__(self, tc_dir="debugger_test_cases"):
        """
        Args:
            tc_dir: Directory containing test code samples

        Test 0: One liner
        Test 1: Simple linear code
        Test 2: Simple function call
        Test 3: Nested function calls
        Test 4: Loop
        Test 5: Function with loop
        Test 6: Recursive function
        Test 7: Multiple sequential functions
        Test 8: Try-except blocks
        Test 9: List comprehensions
        Test 10: Class methods
        """
        tc_code = []           # List of test code strings
        # Read test case files and store in list
        for i in range(NUM_TESTS):
            path = os.path.join(tc_dir, f"tc{i}.py")
            try:
                with open(path, "r") as f:
                    code = f.read()
                    tc_code.append(code)
            except FileNotFoundError:
                print(f"Test case at path {path} not found.")
            except Exception as e:
                print(f"Mysterious error found: {e}")

        df = pd.read_csv(os.path.join(tc_dir, "labels.csv"))
        name = df["filename"].tolist()                      # List of test case names
        trace = df["trace"].tolist()                    # Execution Trace (given)
        trace = [list(map(int, t.split())) for t in trace]
        step_labels = df["step"].tolist()               # List of step labels, where a_i corresponds to the expected output given trace[i]
        step_labels = [list(map(int, t.split())) for t in step_labels]
        step_over_labels = df["step_over"].tolist()     # List of step over labels, where a_i corresponds to the expected output given trace[i]
        step_over_labels = [list(map(int, t.split())) for t in step_over_labels]
        step_out_labels = df["step_out"].tolist()       # List of step out labels, where a_i corresponds to the expected output given trace[i]
        step_out_labels = [list(map(int, t.split())) for t in step_out_labels]

        self.tc = []
        for i in range(len(tc_code)):
            data = {
                "name": name[i],
                "code": tc_code[i],
                "trace": trace[i],
                "step": step_labels[i],
                "step_over": step_over_labels[i],
                "step_out": step_out_labels[i],
            }
            self.tc.append(data)

    def __getitem__(self, index):
        """
        Return the test case at the given index.

        Args:
            index: Index of the test case to retrieve

        Returns:
            A dictionary containing the test case at the given index
        """
        return self.tc[index]
    
    def __len__(self):
        """
        Return the number of test cases
        """
        return len(self.tc)
    
    def __str__(self):
        """
        Return a string representation of the test cases
        """
        return self.tc.__str__()



# ============================================
# TEST CASE CLASS
# ============================================

class DebuggerTestCase:
    """
    Represents a single test case for the debugger.
    """
    
    def __init__(self, idx, tc, breakpoints=[]):
        """
        Args:
            idx: Test code index
            code: Python code string to test
            trace: Expected execution trace (list of line numbers)
            breakpoints: List of breakpoint line numbers (optional)
        """
        self.idx = idx
        if breakpoints is None:
            breakpoints = []
        self.breakpoints = breakpoints

        self.name = tc["name"]
        self.trace = tc["trace"]
        self.code = tc["code"]
        self.step = tc["step"]
        self.step_over = tc["step_over"]
        self.step_out = tc["step_out"]

        self.trace_len = len(self.trace)

        self.breakpoint_labels = [-1 for _ in range(len(self.trace))]
        next_breakpoint_idx = -1
        for i in reversed(range(self.trace_len)):
            self.breakpoint_labels[i] = next_breakpoint_idx
            if self.trace[i] in self.breakpoints:
                next_breakpoint_idx = i

        self.breakpoints = breakpoints if breakpoints else []
        self.code_lines = string_to_lines(self.code)
        self.call_stack_info = analyze_call_stack(self.trace, self.code_lines)
    
    def run_step_test(self, start_line_idx, expected_next_line):
        """
        Test stepping from start_line_idx.
        
        Returns: (success: bool, actual_next_line: int)
        """
        output_next_line = step(self.trace, start_line_idx)
        if output_next_line == None:
            output_next_line = -1
        return (output_next_line == expected_next_line, output_next_line)
    
    def run_step_over_test(self, start_line_idx, expected_next_line):
        """
        Test step over from start_line_idx.
        
        Returns: (success: bool, actual_next_line: int)
        """
        output_next_line = step_over(self.trace, start_line_idx, self.call_stack_info)
        if output_next_line == None:
            output_next_line = -1
        return (output_next_line == expected_next_line, output_next_line)

    def run_step_out_test(self, start_line_idx, expected_next_line):
        """
        Test step out from start_line_idx.
        
        Returns: (success: bool, actual_next_line: int)
        """
        output_next_line = step_out(self.trace, start_line_idx, self.call_stack_info)
        if output_next_line == None:
            output_next_line = -1
        return (output_next_line == expected_next_line, output_next_line)
    
    def run_breakpoint_test(self, start_line_idx, expected_next_line):
        """
        Test stepping from start_line_idx.
        
        Returns: (success: bool, actual_next_line: int)
        """
        output_next_line = continue_to_breakpoint(self.trace, start_line_idx, self.breakpoints)
        if output_next_line == None:
            output_next_line = -1
        return (output_next_line == expected_next_line, output_next_line)
    
    def __call__(self):
        """
        Run step, step over, and step out tests for this test case.
        
        Returns:
            bool: Whether all tests passed successfully
        """
        successful = 0
        total = self.trace_len * 3

        print(f" TEST CASE {self.idx} ({self.name}) ".center(60, "="))
        print()
        print(f"Running step test for tc{self.idx}")
        for i in range(self.trace_len):
            success, actual_next_line = self.run_step_test(i, self.step[i])
            if not success:
                print(f"    Step test failed at trace index {i} (line {self.trace[i]})")
                print(f"        Expected next line: {self.step[i]}")
                print(f"        Actual next line: {actual_next_line}")
            else:
                successful += 1
        print("    Done")

        print(f"Running step over test for tc{self.idx}")
        for i in range(self.trace_len):
            success, actual_next_line = self.run_step_over_test(i, self.step_over[i])
            if not success:
                print(f"    Step over test failed at trace index {i} (line {self.trace[i]})")
                print(f"        Expected next line: {self.step_over[i]}")
                print(f"        Actual next line: {actual_next_line}")
            else:
                successful += 1
        print("    Done")

        print(f"Running step out test for tc{self.idx}")
        for i in range(self.trace_len):
            success, actual_next_line = self.run_step_out_test(i, self.step_out[i])
            if not success:
                print(f"    Step out test failed at trace index {i} (line {self.trace[i]})")
                print(f"        Expected next line: {self.step_out[i]}")
                print(f"        Actual next line: {actual_next_line}")
            else:
                successful += 1
        print("    Done")

        # print(f"Running breakpoint test for tc{self.idx}")
        # for i in range(self.trace_len):
        #     success, actual_next_line = self.run_breakpoint_test(i, self.step_out[i])
        #     if not success:
        #         print(f"    Breakpoint test failed at trace index {i} (line {self.trace[i]})")
        #         print(f"        Expected next line: {self.step_out[i]}")
        #         print(f"        Actual next line: {actual_next_line}")
        #     else:
        #         successful += 1
        # print("    Done")

        print(f"Results: {successful}/{total}")
        print("=" * 60)
        print()
        return successful, total


# ============================================
# TEST RUNNER
# ============================================

class DebuggerTestRunner:
    """
    Runs multiple test cases and reports results.
    """
    
    def __init__(self):
        self.test_cases = []
    
    def add_test(self, idx, tc): 
        """
        Add a test case to the test runner.
        
        Args:
            idx: Test case index
            tc: Test case data (TestCode object)
        """
        self.test_cases.append(DebuggerTestCase(idx, tc))

    def run_all_tests(self):
        """Run all test cases and report results."""
        successful = 0
        total = 0
        for tc in self.test_cases:
            s, t = tc()
            successful += s
            total += t
        print(f"RESULTS: {successful}/{total}")


# ============================================
# INTERACTIVE TESTING
# ============================================

class InteractiveDebugger:
    """
    Interactive debugger for manual testing.
    Paste code and step through it manually.
    """
    
    def __init__(self):
        self.debugger = None
    
    def start_interactive_session(self):
        """
        Start an interactive debugging session.
        User can paste code and step through it.
        """
        # TODO: Implement
        pass
    
    def load_test_case(self, test_case):
        """
        Load a predefined test case for interactive stepping.
        
        Args:
            test_case: DebuggerTestCase object
        """
        # TODO: Implement
        pass
    
    def step(self):
        """Execute step command."""
        # TODO: Implement
        pass
    
    def step_over(self):
        """Execute step over command."""
        # TODO: Implement
        pass
    
    def step_out(self):
        """Execute step out command."""
        # TODO: Implement
        pass
    
    def continue_execution(self):
        """Execute continue command."""
        # TODO: Implement
        pass
    
    def show_state(self):
        """Display current debugger state."""
        # TODO: Implement
        pass
    
    def show_trace(self):
        """Display execution trace so far."""
        # TODO: Implement
        pass


# ============================================
# HELPER FUNCTIONS
# ============================================

def create_mock_trace_output(trace_list):
    """
    Create mock trace output string from trace list.
    For use with DebuggerSession.
    
    Args:
        trace_list: List of line numbers [1, 2, 3, ...]
    
    Returns: String in format "<string>(1)\n<string>(2)\n..."
    """
    # TODO: Implement
    pass


def compare_traces(expected, actual):
    """
    Compare expected trace with actual trace.
    
    Returns: List of differences
    """
    # TODO: Implement
    pass


def print_code_with_trace(code, trace):
    """
    Print code with execution trace annotations.
    Shows which lines executed and how many times.
    """
    # TODO: Implement
    pass


# ============================================
# MAIN - RUN TESTS
# ============================================

if __name__ == "__main__":

    test_code = TestCode("/Users/ethanchen/Desktop/Python Stuff/Visual Debugger/visual-debugger/debugger_test_cases")
    runner = DebuggerTestRunner()

    for i in range(NUM_TESTS):
        runner.add_test(i, test_code[i])

    runner.run_all_tests()



    # print("=" * 60)
    # print("DEBUGGER TESTING FRAMEWORK")
    # print("=" * 60)
    
    # # Example: Create and run a test
    # test1 = DebuggerTestCase(
    #     "Linear Code Test",
    #     TestCode.LINEAR,
    #     TestCode.LINEAR_TRACE
    # )
    
    # print(f"\nTest: {test1.name}")
    # print(f"Code:\n{test1.code}")
    # print(f"Expected trace: {test1.trace}")
    
    # # TODO: Run the test and show results
    
    # print("\n" + "=" * 60)
    # print("To implement:")
    # print("1. Fill in test methods in DebuggerTestCase")
    # print("2. Implement DebuggerTestRunner methods")
    # print("3. Implement InteractiveDebugger")
    # print("4. Add more test cases to TestCode class")
    # print("=" * 60)