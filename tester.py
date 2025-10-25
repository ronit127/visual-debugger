"""
testing.py - Testing framework for debugger_core.py

This file provides a structured way to test the debugger with various code samples.
Easy to add new test cases and verify debugger behavior.

Usage:
    python testing.py
"""

from debugger import get_next_line, string_to_lines, create_debugger_session
import os

# ============================================
# TEST CODE SAMPLES
# ============================================

class TestCode:
    """
    Container for test code samples.
    Add new test cases by adding class variables.
    """
    def __init__(self, tc_dir="debugger_test_cases"):
        """
        Args:
            tc_dir: Directory containing test code samples

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
        self.tc = []

        # Read test case files and store in list
        for i in range(1, 11):
            path = os.path.join(tc_dir, f"tc{i}.py")
            try:
                with open(path, "r") as f:
                    code = f.read()
                    self.tc.append(code)
            except FileNotFoundError:
                print(f"Test case at path {path} not found.")
            except Exception as e:
                print(f"Mysterious error found: {e}")

    def __getitem__(self, index):
        return self.tc[index]
    
    def __len__(self):
        return len(self.tc)
    
    def __str__(self):
        return self.tc.__str__()



# ============================================
# TEST CASE CLASS
# ============================================

class DebuggerTestCase:
    """
    Represents a single test case for the debugger.
    """
    
    def __init__(self, name, code, trace, breakpoints=None):
        """
        Args:
            name: Test case name
            code: Python code string to test
            trace: Expected execution trace (list of line numbers)
            breakpoints: List of breakpoint line numbers (optional)
        """
        self.name = name
        self.code = code
        self.trace = trace
        self.breakpoints = breakpoints if breakpoints else []
        self.code_lines = string_to_lines(code)
    
    def run_step_test(self, start_line, expected_next_line):
        """
        Test stepping from start_line.
        
        Returns: (success: bool, actual_next_line: int)
        """
        # TODO: Implement
        pass
    
    def run_step_over_test(self, start_line, expected_next_line):
        """
        Test step over from start_line.
        
        Returns: (success: bool, actual_next_line: int)
        """
        # TODO: Implement
        pass
    
    def run_full_execution(self, action="step"):
        """
        Run full execution with given action.
        Returns list of all lines visited.
        
        Returns: List of line numbers
        """
        # TODO: Implement
        pass
    
    def verify_trace_matches(self):
        """
        Verify that stepping through entire execution matches expected trace.
        
        Returns: (success: bool, differences: list)
        """
        # TODO: Implement
        pass


# ============================================
# TEST RUNNER
# ============================================

class DebuggerTestRunner:
    """
    Runs multiple test cases and reports results.
    """
    
    def __init__(self):
        self.test_cases = []
        self.results = []
    
    def add_test(self, test_case):
        """Add a test case to run."""
        # TODO: Implement
        pass
    
    def run_all_tests(self):
        """
        Run all registered test cases.
        
        Returns: Summary of results
        """
        # TODO: Implement
        pass
    
    def test_basic_stepping(self):
        """Test basic step functionality."""
        # TODO: Implement
        pass
    
    def test_step_over_functions(self):
        """Test step over functionality."""
        # TODO: Implement
        pass
    
    def test_step_out(self):
        """Test step out functionality."""
        # TODO: Implement
        pass
    
    def test_breakpoints(self):
        """Test continue to breakpoint."""
        # TODO: Implement
        pass
    
    def test_loops(self):
        """Test handling of loops."""
        # TODO: Implement
        pass
    
    def print_results(self):
        """Print test results in readable format."""
        # TODO: Implement
        pass


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
    print("=" * 60)
    print("DEBUGGER TESTING FRAMEWORK")
    print("=" * 60)
    
    # Example: Create and run a test
    test1 = DebuggerTestCase(
        "Linear Code Test",
        TestCode.LINEAR,
        TestCode.LINEAR_TRACE
    )
    
    print(f"\nTest: {test1.name}")
    print(f"Code:\n{test1.code}")
    print(f"Expected trace: {test1.trace}")
    
    # TODO: Run the test and show results
    
    print("\n" + "=" * 60)
    print("To implement:")
    print("1. Fill in test methods in DebuggerTestCase")
    print("2. Implement DebuggerTestRunner methods")
    print("3. Implement InteractiveDebugger")
    print("4. Add more test cases to TestCode class")
    print("=" * 60)