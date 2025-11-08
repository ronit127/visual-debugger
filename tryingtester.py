"""
tester.py - Testing framework for debugger.py

This file provides a structured way to test the debugger with various code samples.
Reads test cases from debugger_test_cases folder.

Usage:
    python tester.py
"""

from debugger import get_next_line, string_to_lines, create_debugger_session
from tracer import generate_trace, generate_trace_from_file
import os

# ============================================
# TEST CODE SAMPLES
# ============================================

class TestCode:
    """
    Container for test code samples.
    Loads from debugger_test_cases directory.
    """
    def __init__(self, tc_dir="debugger_test_cases"):
        """
        Args:
            tc_dir: Directory containing test code samples
        """
        self.tc = []
        self.tc_dir = tc_dir
        self.tc_files = []

        # Read test case files and store in list
        for i in range(1, 11):
            filename = f"tc{i}.py"
            path = os.path.join(tc_dir, filename)
            
            try:
                with open(path, "r") as f:
                    code = f.read()
                    self.tc.append(code)
                    self.tc_files.append(filename)
            except FileNotFoundError:
                self.tc.append(None)
                self.tc_files.append(None)
            except Exception as e:
                print(f"Error reading {path}: {e}")
                self.tc.append(None)
                self.tc_files.append(None)

    def __getitem__(self, index):
        """Get test case by index (0-based)"""
        if 0 <= index < len(self.tc):
            return self.tc[index]
        return None
    
    def __len__(self):
        return len(self.tc)
    
    def __str__(self):
        available = sum(1 for tc in self.tc if tc is not None)
        return f"TestCode: {available}/{len(self.tc)} test cases loaded from {self.tc_dir}/"
    
    def get_test(self, num):
        """Get test case by number (1-10)"""
        if 1 <= num <= 10:
            return self.tc[num - 1]
        return None
    
    def get_test_info(self, num):
        """Get test case info including filename"""
        if 1 <= num <= 10:
            return {
                'code': self.tc[num - 1],
                'filename': self.tc_files[num - 1],
                'number': num
            }
        return None


# ============================================
# TEST CASE CLASS
# ============================================

class DebuggerTestCase:
    """
    Represents a single test case for the debugger.
    """
    
    def __init__(self, name, code, trace=None, breakpoints=None):
        """
        Args:
            name: Test case name
            code: Python code string to test
            trace: Expected execution trace (list of line numbers) - optional, will be generated
            breakpoints: List of breakpoint line numbers (optional)
        """
        self.name = name
        self.code = code
        self.breakpoints = breakpoints if breakpoints else []
        self.code_lines = string_to_lines(code)
        self.error = None
        self.output = None
        
        # Generate trace if not provided
        if trace is None:
            self.trace, self.output, self.error = generate_trace(code)
        else:
            self.trace = trace
    
    def has_error(self):
        """Check if test case has compilation or runtime error"""
        return self.error is not None
    
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
    
    # Load test cases from files
    test_code = TestCode()
    print(f"\n{test_code}")
    
    # Test each available test case
    for i in range(1, 11):
        test_info = test_code.get_test_info(i)
        
        if test_info['code'] is None:
            continue
        
        print(f"\n{'=' * 60}")
        print(f"TEST CASE {i}: {test_info['filename']}")
        print(f"{'=' * 60}")
        
        # Create test case
        test_case = DebuggerTestCase(
            f"Test Case {i}",
            test_info['code']
        )
        
        # Show code preview
        lines = test_info['code'].split('\n')
        preview_lines = min(5, len(lines))
        print(f"\nCode preview (first {preview_lines} lines):")
        for j, line in enumerate(lines[:preview_lines], 1):
            print(f"  {j}: {line}")
        if len(lines) > preview_lines:
            print(f"  ... ({len(lines) - preview_lines} more lines)")
        
        # Check for errors
        if test_case.has_error():
            print(f"\nERROR: {test_case.error}")
            print(f"Output: {test_case.output}")
            continue
        
        # Show trace info
        print(f"\n✓ Trace generated: {len(test_case.trace)} steps")
        print(f"  Trace: {test_case.trace[:20]}{'...' if len(test_case.trace) > 20 else ''}")
        
        if test_case.output:
            print(f"\nProgram output:")
            print(f"  {test_case.output.strip()}")
        
        # Try to debug it
        try:
            print(f"\n--- Testing Debugger ---")
            debugger = create_debugger_session()
            debugger.start_session(test_case.code, test_case.trace, [])
            
            state = debugger.get_state()
            print(f"Initial line: {state['current_line']}")
            
            # Step 3 times or until complete
            max_steps = min(3, len(test_case.trace))
            for step_num in range(max_steps):
                result = debugger.execute_action("step")
                if result['status'] == 'complete':
                    print(f"  Step {step_num + 1}: Execution complete")
                    break
                print(f"  Step {step_num + 1}: Line {result['next_line']} (depth {result['depth']})")
            
            print(f"Debugger test passed for {test_info['filename']}")
            
        except Exception as e:
            print(f"Debugger error: {str(e)}")
    
    print("\n" + "=" * 60)
    print("TESTING COMPLETE")
    print("=" * 60)
    print("\nTO IMPLEMENT:")
    print("1. Fill in test methods in DebuggerTestCase")
    print("2. Implement DebuggerTestRunner methods")
    print("3. Implement InteractiveDebugger")
    print("4. Add more test case files in debugger_test_cases/")
    print("=" * 60)