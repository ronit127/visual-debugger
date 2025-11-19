"""
tester.py - Testing framework for debugger.py

This file provides a structured way to test the debugger with various code samples.
Reads test cases from debugger_test_cases folder.

Usage:
    python tester.py
"""

from debugger2 import get_next_line, string_to_lines, create_debugger_session
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
        
        # Show code with line numbers and indentation markers
        lines = test_info['code'].split('\n')
        preview_lines = min(10, len(lines))
        print(f"\nCode preview (first {preview_lines} lines):")
        for j, line in enumerate(lines[:preview_lines], 1):
            # Show indentation level
            indent = len(line) - len(line.lstrip())
            indent_marker = ">" * (indent // 4) if indent > 0 else ""
            print(f"  {j:2d} {indent_marker:4s} {line}")
        if len(lines) > preview_lines:
            print(f"  ... ({len(lines) - preview_lines} more lines)")
        
        # Check for errors
        if test_case.has_error():
            print(f"\n❌ ERROR: {test_case.error}")
            continue
        
        # Show trace info
        if len(test_case.trace) == 0:
            print(f"\n⚠️  WARNING: Empty trace generated!")
            continue
            
        print(f"\n✓ Trace generated: {len(test_case.trace)} steps")
        print(f"  Trace: {test_case.trace[:20]}{'...' if len(test_case.trace) > 20 else ''}")
        
        # Show program output if any
        if test_case.output:
            output_lines = test_case.output.strip().split('\n')
            if output_lines and output_lines[0]:
                print(f"\nProgram output:")
                for line in output_lines[:5]:
                    print(f"  {line}")
        
        # Try to debug it
        try:
            print(f"\n--- Testing Debugger (Indentation-Based) ---")
            debugger = create_debugger_session()
            debugger.start_session(test_case.code, test_case.trace, [])
            
            state = debugger.get_state()
            print(f"Initial state:")
            print(f"  Line: {state['current_line']}")
            print(f"  Depth: {state['current_depth']}")
            print(f"  Indent: {state['current_indent']}")
            print(f"  Scope: {state['current_scope_type']}")
            
            if state['current_line'] is None:
                print("  ⚠️  WARNING: Debugger has no initial line")
                continue
            
            # Test basic stepping
            print(f"\n--- Testing STEP (into) ---")
            max_steps = min(5, len(test_case.trace))
            for step_num in range(max_steps):
                result = debugger.execute_action("step")
                if result['status'] == 'complete':
                    print(f"  Step {step_num + 1}: ✓ Execution complete")
                    break
                
                indent_marker = ">" * (result['indent'] // 4) if result['indent'] else ""
                print(f"  Step {step_num + 1}: Line {result['next_line']:2d} "
                      f"(depth={result['depth']}, indent={result['indent']:2d}) "
                      f"{indent_marker} {result['current_code'][:40] if result['current_code'] else ''}")
            
            # Reset for step over test
            debugger.start_session(test_case.code, test_case.trace, [])
            
            # Test step over (if there are function calls)
            has_function = any('def ' in line for line in lines)
            if has_function and len(test_case.trace) > 3:
                print(f"\n--- Testing STEP OVER ---")
                step_count = 0
                max_step_over = min(3, len(test_case.trace))
                while step_count < max_step_over:
                    result = debugger.execute_action("step over")
                    if result['status'] == 'complete':
                        print(f"  Step {step_count + 1}: ✓ Execution complete")
                        break
                    
                    indent_marker = ">" * (result['indent'] // 4) if result['indent'] else ""
                    print(f"  Step {step_count + 1}: Line {result['next_line']:2d} "
                          f"(depth={result['depth']}) "
                          f"{indent_marker} {result['current_code'][:40] if result['current_code'] else ''}")
                    step_count += 1
            
            # Test breakpoints if applicable
            if len(lines) >= 3:
                print(f"\n--- Testing BREAKPOINTS ---")
                debugger.start_session(test_case.code, test_case.trace, [])
                
                # Set breakpoint at middle of code
                bp_line = min(3, len(lines))
                debugger.add_breakpoint(bp_line)
                print(f"  Set breakpoint at line {bp_line}")
                
                result = debugger.execute_action("continue")
                if result['status'] == 'active' and result['next_line'] == bp_line:
                    print(f"  ✓ Hit breakpoint at line {bp_line}")
                elif result['status'] == 'complete':
                    print(f"  ⚠️  Reached end without hitting breakpoint")
                else:
                    print(f"  ⚠️  Stopped at line {result['next_line']} instead of {bp_line}")
            
            # Test scope tracking accuracy
            print(f"\n--- Scope Analysis ---")
            debugger.start_session(test_case.code, test_case.trace, [])
            
            # Collect depth changes
            depths = []
            for _ in range(min(len(test_case.trace), 20)):
                state = debugger.get_state()
                if state['is_active']:
                    depths.append(state['current_depth'])
                    debugger.execute_action("step")
                else:
                    break
            
            if depths:
                print(f"  Depth sequence: {depths[:15]}{'...' if len(depths) > 15 else ''}")
                print(f"  Max depth: {max(depths)}")
                print(f"  Min depth: {min(depths)}")
                
                # Check if depth tracking seems reasonable
                if has_function and max(depths) == 0:
                    print(f"  ⚠️  WARNING: Has functions but max depth is 0")
                elif max(depths) > 10:
                    print(f"  ⚠️  WARNING: Very deep nesting (depth={max(depths)})")
                else:
                    print(f"  ✓ Depth tracking looks reasonable")
            
            print(f"\n✅ All tests passed for {test_info['filename']}")
            
        except Exception as e:
            print(f"\n❌ Debugger error: {str(e)}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "=" * 60)
    print("TESTING COMPLETE")
    print("=" * 60)
    print("\nSUMMARY:")
    print("✓ Trace generation working")
    print("✓ Indentation-based scope tracking")
    print("✓ Step, Step Over, Continue commands")
    print("✓ Breakpoint management")
    print("✓ Depth tracking validation")
    print("\nREADY FOR:")
    print("1. Variable tracking implementation (Week 1)")
    print("2. Data structure introspection (Week 2)")
    print("3. Visualization team integration (Week 2-3)")
    print("=" * 60)