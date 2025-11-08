"""
debugger_core.py - Pure debugger functionality (Backend Team)
"""

import re

# ============================================
# MAIN DEBUGGER INTERFACE
# ============================================

def get_next_line(breakpoints, current_line, action, code_lines, trace_list):
    """
    Core debugger function - determines next line to execute.
    
    Args:
        breakpoints: List of line numbers with breakpoints [3, 7, 12]
        current_line: Current line number (1-indexed)
        action: "step", "step into", "step over", "step out", "continue"
        code_lines: List of code lines (use string_to_lines() to convert)
        trace_list: Execution trace - line numbers in order [1,2,3,5,6,3,4,...]
    
    Returns:
        Next line number to pause at, or None if execution complete
    """

    # Find current position in trace
    current_index = find_current_index(trace_list, current_line)
    if current_index == -1:
        return None
    
    # Build call stack info for sophisticated stepping
    call_stack_info = analyze_call_stack(trace_list, code_lines)
    
    # Execute action
    if action == "step":
        return step(trace_list, current_index)
    elif action == "step over":
        return step_over(trace_list, current_index, call_stack_info)
    elif action == "step out":
        return step_out(trace_list, current_index, call_stack_info)
    elif action == "continue":
        return continue_to_breakpoint(trace_list, current_index, breakpoints)
    else:
        return step(trace_list, current_index)


# ============================================
# STEPPING FUNCTIONS
# ============================================

def step(trace_list, current_index):
    """
    Step to next line (step into functions).
    
    Returns: Next line number or None
    """
    if current_index + 1 < len(trace_list):
        return trace_list[current_index + 1]
    return None


def step_over(trace_list, current_index, call_stack_info):
    """
    Step over function calls - skip function internals.
    
    Args:
        trace_list: Full execution trace
        current_index: Current position in trace
        call_stack_info: Pre-analyzed call stack data
    
    Returns: Next line number at same or lower depth
    """
    if current_index + 1 >= len(trace_list):
        return None
    
    current_depth = call_stack_info[current_index].get('depth', 0)
    
    # Check if we're about to enter a function
    next_depth = call_stack_info.get(current_index + 1, {}).get('depth', 0)
    
    if next_depth > current_depth:
        # Entering function - skip to where we exit
        for i in range(current_index + 1, len(trace_list)):
            if call_stack_info[i].get('depth', 0) <= current_depth:
                return trace_list[i]
        return None
    
    # Not entering function, just step normally
    return trace_list[current_index + 1]


def step_out(trace_list, current_index, call_stack_info):
    """
    Step out of current function - return to caller.
    
    Returns: First line after exiting current function
    """
    if current_index + 1 >= len(trace_list):
        return None
    
    current_depth = call_stack_info[current_index].get('depth', 0)
    
    # Find where depth decreases (exit current function)
    for i in range(current_index + 1, len(trace_list)):
        if call_stack_info[i].get('depth', 0) < current_depth:
            return trace_list[i]
    
    return None


def continue_to_breakpoint(trace_list, current_index, breakpoints):
    """
    Continue execution until hitting next breakpoint.
    
    Returns: Next breakpoint line or None
    """
    for i in range(current_index + 1, len(trace_list)):
        if trace_list[i] in breakpoints:
            return trace_list[i]
    return None


# ============================================
# CALL STACK ANALYZER (Person 2 - Week 3)
# ============================================

def analyze_call_stack(trace_list, code_lines):
    """
    Analyze trace to build call stack information.
    This enables robust step-over and step-out.
    
    Args:
        trace_list: Execution trace
        code_lines: Source code lines
    
    Returns:
        Dict mapping trace_index -> {
            'depth': call depth,
            'action': 'enter'/'exit'/None,
            'line': line number
        }
    """
    call_stack = {}
    current_depth = 0
    
    for i in range(len(trace_list)):
        line_num = trace_list[i]
        
        # Determine if entering or exiting function
        action = None
        if i < len(trace_list) - 1:
            next_line = trace_list[i + 1]
            
            if is_function_call(line_num, next_line, code_lines):
                action = 'enter'
                current_depth += 1
            elif is_function_return(line_num, next_line, i, trace_list):
                action = 'exit'
                current_depth = max(0, current_depth - 1)
        
        call_stack[i] = {
            'depth': current_depth,
            'action': action,
            'line': line_num
        }
    
    return call_stack


def is_function_call(curr_line, next_line, code_lines):
    """
    Detect if current line is calling a function.
    
    Heuristic: Line has function call syntax and jumps backward to function def.
    """
    if curr_line > len(code_lines):
        return False
    
    code = code_lines[curr_line - 1].strip()
    
    # Has parentheses (function call)
    has_call = '(' in code and ')' in code
    # Not a function definition
    not_def = not code.startswith('def ')
    # Not control flow
    not_control = not any(code.startswith(kw) for kw in ['if ', 'elif ', 'while ', 'for ', 'with '])
    # Jumps to earlier line (function definition location)
    jumps_back = next_line < curr_line
    
    return has_call and not_def and not_control and jumps_back


def is_function_return(curr_line, next_line, trace_idx, trace_list):
    """
    Detect if we're returning from a function.
    
    Heuristic: Were in lower line numbers, now jumping forward significantly.
    """
    if trace_idx < 3:
        return False
    
    # Look at recent execution history
    recent_lines = trace_list[max(0, trace_idx - 3):trace_idx]
    
    if recent_lines:
        was_in_lower_lines = max(recent_lines) < curr_line
        jumping_forward = next_line > curr_line + 1
        return was_in_lower_lines and jumping_forward
    
    return False


# ============================================
# UTILITY FUNCTIONS
# ============================================

def find_current_index(trace_list, current_line, last_index=0):
    """
    Find index of current_line in trace, starting from last_index.
    Handles loops where same line appears multiple times.
    
    Args:
        trace_list: Execution trace
        current_line: Line to find
        last_index: Start searching from this index (for loop handling)
    
    Returns:
        Index in trace_list, or -1 if not found
    """
    try:
        for i in range(last_index, len(trace_list)):
            if trace_list[i] == current_line:
                return i
        return -1
    except:
        return -1


def string_to_lines(code_string):
    """Convert code string to list of lines."""
    return code_string.splitlines()



# ============================================
# DEBUGGER STATE CLASS
# ============================================

class DebuggerSession:
    """
    Stateful debugger session for easier management.
    Tracks execution position, handles loops, provides hooks for visualization.
    """
    
    def __init__(self):
        self.trace_list = []
        self.code_lines = []
        self.breakpoints = []
        self.current_line = None
        self.current_index = 0
        self.call_stack_info = {}
        self.is_active = False
        
        # Hook for visualization team - they can register callbacks
        self.on_step_callbacks = []
        self.execution_history = []
    
    # need to add generate_trace function from trace_generator.py
    def start_session(self, code, trace, breakpoints):
        """
        Initialize debugging session.
        Args:
            code: Source code as a string.
            trace: Execution trace as a list of line numbers.
            breakpoints: List of line numbers with breakpoints.
        """
        self.code_lines = string_to_lines(code)
        self.trace_list = trace
        self.breakpoints = breakpoints
        self.current_line = trace[0] if trace else None
        self.current_index = 0
        self.call_stack_info = analyze_call_stack(trace, self.code_lines)
        self.is_active = True
        self.execution_history = []

    def execute_action(self, action):
        """
        Execute debugger action.
        Args:
            action: Debugger action ("step", "step over", "step out", "continue").
        Returns:
            Result dictionary with next line, status, and additional info.
        """
        if not self.is_active:
            return self._create_result(None, "inactive")

        next_line = get_next_line(
            self.breakpoints,
            self.current_line,
            action,
            self.code_lines,
            self.trace_list
        )

        if next_line is None:
            self.is_active = False
            return self._create_result(None, "complete")

        self.current_line = next_line
        self.current_index = find_current_index(self.trace_list, next_line, self.current_index)
        self.execution_history.append(next_line)
        self._trigger_callbacks("step", next_line)
        return self._create_result(next_line, "active")

    def _create_result(self, next_line, status):
        """
        Create standardized result dictionary.
        Args:
            next_line: Next line number to execute.
            status: Status of the debugger ("active", "complete", "inactive").
        Returns:
            Dictionary with debugger state.
        """
        return {
            "next_line": next_line,
            "status": status,
            "current_code": self.code_lines[next_line - 1] if next_line and next_line <= len(self.code_lines) else None,
            "depth": self.call_stack_info[self.current_index]['depth'] if next_line and self.current_index in self.call_stack_info else None
        }

    def register_callback(self, callback):
        """
        Register callback for visualization team.
        Args:
            callback: Function to call on debugger events.
        """
        self.on_step_callbacks.append(callback)

    def _trigger_callbacks(self, event_type, line_num):
        """
        Trigger all registered callbacks.
        Args:
            event_type: Type of event ("step", "breakpoint", etc.).
            line_num: Line number associated with the event.
        """
        for callback in self.on_step_callbacks:
            callback(event_type, line_num)

    def get_state(self):
        """
        Get current debugger state for visualization/frontend.
        Returns:
            Dictionary with current debugger state.
        """
        return {
            "current_line": self.current_line,
            "breakpoints": self.breakpoints,
            "is_active": self.is_active,
            "execution_history": self.execution_history
        }

    def add_breakpoint(self, line_num):
        """
        Add breakpoint at the specified line.
        Args:
            line_num: Line number to add a breakpoint.
        """
        if line_num not in self.breakpoints:
            self.breakpoints.append(line_num)

    def remove_breakpoint(self, line_num):
        """
        Remove breakpoint at the specified line.
        Args:
            line_num: Line number to remove the breakpoint.
        """
        if line_num in self.breakpoints:
            self.breakpoints.remove(line_num)


# ============================================
# INTERFACE FOR OTHER TEAMS
# ============================================

def create_debugger_session():
    """
    Factory function for other teams to create debugger sessions.
    
    Usage example for visualization team:
        debugger = create_debugger_session()
        debugger.start_session(code, trace, [3, 7])
        
        def my_visualization_callback(event, line):
            print(f"Visualization: {event} at line {line}")
        
        debugger.register_callback(my_visualization_callback)
        result = debugger.execute_action("step")
    """
    return DebuggerSession()