"""
debugger.py - Pure debugger functionality (Backend Team)

Robust implementation using Python indentation for scope tracking.
"""

import re

# ============================================
# MAIN DEBUGGER INTERFACE
# ============================================

def get_next_line(breakpoints, current_line, action, code_lines, trace_list, current_index=None):
    """
    Core debugger function - determines next line to execute.
    
    Args:
        breakpoints: List of line numbers with breakpoints [3, 7, 12]
        current_line: Current line number (1-indexed)
        action: "step", "step over", "step out", "continue"
        code_lines: List of code lines (use string_to_lines() to convert)
        trace_list: Execution trace - line numbers in order [1,2,3,5,6,3,4,...]
        current_index: Optional current position in trace (for efficiency)
    
    Returns:
        Next line number to pause at, or None if execution complete
    """
    # Find current position in trace
    if current_index is None:
        current_index = find_current_index(trace_list, current_line, 0)
    
    if current_index == -1 or current_index >= len(trace_list) - 1:
        return None
    
    # Build call stack info using indentation analysis
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
    Simple: just go to next trace entry.
    
    Returns: Next line number or None
    """
    if current_index + 1 < len(trace_list):
        return trace_list[current_index + 1]
    return None


def step_over(trace_list, current_index, call_stack_info):
    """
    Step over function calls - skip function internals.
    Continue until we return to same or shallower depth.
    
    Args:
        trace_list: Full execution trace
        current_index: Current position in trace
        call_stack_info: Pre-analyzed call stack data
    
    Returns: Next line number at same or lower depth
    """
    if current_index + 1 >= len(trace_list):
        return None
    
    current_depth = call_stack_info[current_index]['depth']
    
    # Find next execution point at same or lower depth
    for i in range(current_index + 1, len(trace_list)):
        if call_stack_info[i]['depth'] <= current_depth:
            return trace_list[i]
    
    # Reached end of execution
    return None


def step_out(trace_list, current_index, call_stack_info):
    """
    Step out of current function - return to caller.
    Continue until depth decreases (we exit current function).
    
    Returns: First line after exiting current function
    """
    if current_index + 1 >= len(trace_list):
        return None
    
    current_depth = call_stack_info[current_index]['depth']
    
    # If already at depth 0, can't step out
    if current_depth == 0:
        return None
    
    # Find where depth decreases below current
    for i in range(current_index + 1, len(trace_list)):
        if call_stack_info[i]['depth'] < current_depth:
            return trace_list[i]
    
    return None


def continue_to_breakpoint(trace_list, current_index, breakpoints):
    """
    Continue execution until hitting next breakpoint.
    
    Returns: Next breakpoint line or None
    """
    if not breakpoints:
        return None
    
    for i in range(current_index + 1, len(trace_list)):
        if trace_list[i] in breakpoints:
            return trace_list[i]
    
    return None


# ============================================
# INDENTATION-BASED SCOPE ANALYSIS
# ============================================

def get_indentation_level(line):
    """
    Get indentation level of a line.
    
    Args:
        line: String line of code
    
    Returns:
        Number of spaces of indentation (tabs counted as 4 spaces)
    """
    if not line:
        return 0
    
    # Count leading whitespace
    indent = 0
    for char in line:
        if char == ' ':
            indent += 1
        elif char == '\t':
            indent += 4  # Standard Python tab = 4 spaces
        else:
            break
    
    return indent


def is_scope_defining_line(line):
    """
    Check if line defines a new scope (function, class, loop, conditional, etc.).
    
    Args:
        line: String line of code
    
    Returns:
        True if line ends with ':' and defines scope
    """
    stripped = line.strip()
    
    if not stripped or stripped.startswith('#'):
        return False
    
    # Check if line ends with colon (scope definition)
    if not stripped.endswith(':'):
        return False
    
    # Check for scope-defining keywords
    scope_keywords = ['def ', 'class ', 'if ', 'elif ', 'else:', 'for ', 
                      'while ', 'try:', 'except ', 'except:', 'finally:', 
                      'with ', 'match ', 'case ']
    
    return any(stripped.startswith(kw) for kw in scope_keywords)


def is_function_definition(line):
    """Check if line is a function or class definition."""
    stripped = line.strip()
    return stripped.startswith('def ') or stripped.startswith('class ')


def build_scope_map(code_lines):
    """
    Build a map of line numbers to their scope level and type.
    Uses indentation to determine scope depth.
    
    Args:
        code_lines: List of code lines
    
    Returns:
        Dict mapping line_number -> {
            'indent': indentation level,
            'scope_type': 'function'/'class'/'control'/'module',
            'is_scope_start': bool
        }
    """
    scope_map = {}
    
    for line_num in range(1, len(code_lines) + 1):
        line = code_lines[line_num - 1]
        
        indent = get_indentation_level(line)
        is_scope_start = is_scope_defining_line(line)
        
        # Determine scope type
        scope_type = 'module'
        if is_scope_start:
            if is_function_definition(line):
                scope_type = 'function'
            else:
                scope_type = 'control'  # if, for, while, etc.
        
        scope_map[line_num] = {
            'indent': indent,
            'scope_type': scope_type,
            'is_scope_start': is_scope_start
        }
    
    return scope_map


def analyze_call_stack(trace_list, code_lines):
    """
    Analyze trace to build call stack information using indentation.
    
    This is the ROBUST implementation:
    - Uses Python's indentation to determine scope depth
    - Tracks when we enter/exit functions based on indentation changes
    - Uses a stack to properly track nested function calls
    
    Args:
        trace_list: Execution trace
        code_lines: Source code lines
    
    Returns:
        Dict mapping trace_index -> {
            'depth': call depth (0 = main, 1+ = nested functions),
            'line': line number,
            'indent': indentation level,
            'scope_type': type of scope we're in
        }
    """
    if not trace_list:
        return {}
    
    # Build scope map from source code
    scope_map = build_scope_map(code_lines)
    
    call_stack_info = {}
    
    # Stack to track function call depth
    # Each entry: {'line': line_num, 'indent': indent_level, 'type': scope_type}
    call_stack = []
    
    # Track previous line for detecting transitions
    prev_line = None
    prev_indent = 0
    
    for i in range(len(trace_list)):
        line_num = trace_list[i]
        
        # Get scope info for current line
        if line_num not in scope_map:
            # Invalid line number, use safe defaults
            scope_info = {'indent': 0, 'scope_type': 'module', 'is_scope_start': False}
        else:
            scope_info = scope_map[line_num]
        
        curr_indent = scope_info['indent']
        
        if i > 0 and prev_line is not None:
            # Detect scope changes based on execution flow
            
            # Case 1: Jumped to function definition (backward jump to 'def' line)
            if line_num < prev_line and scope_info['is_scope_start'] and scope_info['scope_type'] == 'function':
                # Entering a function - push onto stack
                call_stack.append({
                    'line': line_num,
                    'indent': curr_indent,
                    'type': 'function'
                })
            
            # Case 2: Indentation decreased significantly - exiting scope(s)
            elif curr_indent < prev_indent:
                # Pop stack until we match indentation
                while call_stack and call_stack[-1]['indent'] >= curr_indent:
                    # Only pop if we're truly exiting (not just unindenting in same scope)
                    if call_stack[-1]['type'] == 'function':
                        call_stack.pop()
                    else:
                        break
            
            # Case 3: Forward jump out of function body - function return
            elif prev_line is not None and line_num > prev_line:
                # Check if we jumped forward past the function we were in
                if call_stack:
                    # If we jumped to a line with lower indent than current function, we returned
                    if curr_indent <= call_stack[-1]['indent']:
                        # Pop functions until indent matches
                        while call_stack and call_stack[-1]['indent'] >= curr_indent:
                            if call_stack[-1]['type'] == 'function':
                                call_stack.pop()
                            else:
                                break
        
        # Current depth is the size of call stack
        depth = len([frame for frame in call_stack if frame['type'] == 'function'])
        
        # Store info
        call_stack_info[i] = {
            'depth': depth,
            'line': line_num,
            'indent': curr_indent,
            'scope_type': scope_info['scope_type']
        }
        
        # Update previous state
        prev_line = line_num
        prev_indent = curr_indent
    
    return call_stack_info


# ============================================
# UTILITY FUNCTIONS
# ============================================

def find_current_index(trace_list, current_line, last_index=0):
    """
    Find the NEXT occurrence of current_line in trace after last_index.
    Critical for handling loops where the same line executes multiple times.
    
    Args:
        trace_list: Execution trace
        current_line: Line to find
        last_index: Start searching from this index (exclusive)
    
    Returns:
        Index in trace_list, or -1 if not found
    """
    if not trace_list or last_index >= len(trace_list):
        return -1
    
    # Search from last_index onwards
    for i in range(last_index, len(trace_list)):
        if trace_list[i] == current_line:
            return i
    
    return -1


def string_to_lines(code_string):
    """Convert code string to list of lines."""
    if not code_string:
        return []
    return code_string.splitlines()


# ============================================
# DEBUGGER STATE CLASS
# ============================================

class DebuggerSession:
    """
    Stateful debugger session for easier management.
    Tracks execution position, handles loops, provides hooks for visualization.
    
    Design supports future features:
    - Variable tracking (add variable_snapshots dict)
    - Scope management (add scope_stack)
    - Expression evaluation (add eval_in_context method)
    """
    
    def __init__(self):
        # Core execution state
        self.trace_list = []
        self.code_lines = []
        self.breakpoints = []
        self.current_line = None
        self.current_index = 0
        
        # Pre-computed analysis
        self.call_stack_info = {}
        self.scope_map = {}  # Indentation-based scope info
        
        # Session state
        self.is_active = False
        self.execution_history = []
        
        # Hooks for visualization team
        self.on_step_callbacks = []
        
        # Reserved for future features (Week 1 Person 1)
        self._variable_snapshots = {}  # Will store variable state at each step
        self._scope_stack = []  # Will track scope for variable lookup
    
    def start_session(self, code, trace, breakpoints=None):
        """
        Initialize debugging session.
        
        Args:
            code: Source code as a string
            trace: Execution trace as a list of line numbers
            breakpoints: List of line numbers with breakpoints (optional)
        """
        if not trace:
            raise ValueError("Cannot start session with empty trace")
        
        self.code_lines = string_to_lines(code)
        self.trace_list = trace
        self.breakpoints = breakpoints if breakpoints else []
        self.current_line = trace[0]
        self.current_index = 0
        
        # Build scope and call stack info
        self.scope_map = build_scope_map(self.code_lines)
        self.call_stack_info = analyze_call_stack(trace, self.code_lines)
        
        self.is_active = True
        self.execution_history = [trace[0]]
        
        # Trigger initial state callback
        self._trigger_callbacks("start", self.current_line)

    def execute_action(self, action):
        """
        Execute debugger action and advance state.
        
        Args:
            action: "step", "step over", "step out", "continue"
        
        Returns:
            Dict with keys:
                - next_line: Next line number (or None if complete)
                - status: "active", "complete", or "inactive"
                - current_code: Code at current line
                - depth: Call stack depth
                - indent: Indentation level
                - index: Position in trace
        """
        if not self.is_active:
            return self._create_result(None, "inactive", self.current_index)
        
        # Get next line using core debugger logic
        next_line = get_next_line(
            self.breakpoints,
            self.current_line,
            action,
            self.code_lines,
            self.trace_list,
            self.current_index
        )
        
        if next_line is None:
            self.is_active = False
            return self._create_result(None, "complete", self.current_index)
        
        # Update state - CRITICAL: advance index properly for loops
        old_index = self.current_index
        self.current_index = find_current_index(self.trace_list, next_line, old_index + 1)
        
        # Validation: ensure we found the next occurrence
        if self.current_index == -1:
            # This shouldn't happen with valid trace
            self.is_active = False
            return self._create_result(None, "error", old_index)
        
        self.current_line = next_line
        self.execution_history.append(next_line)
        
        # Determine event type for callbacks
        event_type = "step"
        if action == "continue" and next_line in self.breakpoints:
            event_type = "breakpoint"
        
        self._trigger_callbacks(event_type, next_line)
        
        return self._create_result(next_line, "active", self.current_index)

    def _create_result(self, next_line, status, index):
        """
        Create standardized result dictionary with proper bounds checking.
        
        Args:
            next_line: Next line number to execute (or None)
            status: "active", "complete", "inactive", "error"
            index: Current index in trace
        
        Returns:
            Dictionary with debugger state including indentation info
        """
        result = {
            "next_line": next_line,
            "status": status,
            "current_code": None,
            "depth": None,
            "indent": None,
            "scope_type": None,
            "index": index
        }
        
        # Safe retrieval with bounds checking
        if next_line and 0 < next_line <= len(self.code_lines):
            result["current_code"] = self.code_lines[next_line - 1]
            
            # Add scope info
            if next_line in self.scope_map:
                result["indent"] = self.scope_map[next_line]['indent']
                result["scope_type"] = self.scope_map[next_line]['scope_type']
        
        if index in self.call_stack_info:
            result["depth"] = self.call_stack_info[index]['depth']
        
        return result

    def step_back(self):
        """
        Step backward in execution (time-travel debugging).
        Uses execution history to go to previous state.
        
        Returns:
            Result dictionary like execute_action
        """
        if len(self.execution_history) <= 1:
            # Can't go back from first step
            return self._create_result(self.current_line, "active", self.current_index)
        
        # Remove current state
        self.execution_history.pop()
        
        # Get previous state
        prev_line = self.execution_history[-1]
        
        # Find the correct index for this step in history
        # Need to find the nth occurrence where n = len(execution_history)
        count = 0
        target_count = sum(1 for line in self.execution_history if line == prev_line)
        
        for i in range(len(self.trace_list)):
            if self.trace_list[i] == prev_line:
                count += 1
                if count == target_count:
                    self.current_index = i
                    self.current_line = prev_line
                    break
        
        self._trigger_callbacks("step_back", prev_line)
        return self._create_result(prev_line, "active", self.current_index)

    def register_callback(self, callback):
        """
        Register callback for events.
        Callback signature: callback(event_type: str, line_num: int)
        
        Event types: "start", "step", "breakpoint", "step_back"
        """
        if callable(callback):
            self.on_step_callbacks.append(callback)

    def _trigger_callbacks(self, event_type, line_num):
        """Trigger all registered callbacks with error handling."""
        for callback in self.on_step_callbacks:
            try:
                callback(event_type, line_num)
            except Exception as e:
                # Don't let callback errors crash debugger
                print(f"Warning: Callback error: {e}")

    def get_state(self):
        """
        Get current debugger state for visualization/frontend.
        
        Returns:
            Dictionary with complete current state including scope info
        """
        state = {
            "current_line": self.current_line,
            "current_index": self.current_index,
            "breakpoints": self.breakpoints.copy(),
            "is_active": self.is_active,
            "execution_history": self.execution_history.copy(),
            "total_steps": len(self.trace_list),
            "current_depth": 0,
            "current_indent": 0,
            "current_scope_type": "module"
        }
        
        # Add current scope info
        if self.current_index in self.call_stack_info:
            state["current_depth"] = self.call_stack_info[self.current_index]['depth']
            state["current_indent"] = self.call_stack_info[self.current_index]['indent']
            state["current_scope_type"] = self.call_stack_info[self.current_index]['scope_type']
        
        return state

    def get_scope_info(self, line_num):
        """
        Get scope information for a specific line.
        Useful for variable tracking to determine which scope variables belong to.
        
        Args:
            line_num: Line number to query
        
        Returns:
            Dict with indent, scope_type, is_scope_start
        """
        return self.scope_map.get(line_num, {
            'indent': 0,
            'scope_type': 'module',
            'is_scope_start': False
        })

    def add_breakpoint(self, line_num):
        """
        Add breakpoint at specified line.
        Validates line number is in valid range.
        """
        if not (1 <= line_num <= len(self.code_lines)):
            raise ValueError(f"Invalid line number: {line_num}")
        
        if line_num not in self.breakpoints:
            self.breakpoints.append(line_num)
            self.breakpoints.sort()  # Keep sorted for efficiency

    def remove_breakpoint(self, line_num):
        """Remove breakpoint at specified line."""
        if line_num in self.breakpoints:
            self.breakpoints.remove(line_num)

    def toggle_breakpoint(self, line_num):
        """Toggle breakpoint at specified line."""
        if line_num in self.breakpoints:
            self.remove_breakpoint(line_num)
            return False
        else:
            self.add_breakpoint(line_num)
            return True

    def clear_all_breakpoints(self):
        """Remove all breakpoints."""
        self.breakpoints.clear()

    def run_to_line(self, target_line):
        """
        Continue execution until reaching target line.
        
        Args:
            target_line: Line number to stop at
        
        Returns:
            Result dictionary
        """
        if not self.is_active:
            return self._create_result(None, "inactive", self.current_index)
        
        # Temporarily add breakpoint
        temp_bp = target_line not in self.breakpoints
        if temp_bp:
            self.add_breakpoint(target_line)
        
        # Continue to breakpoint
        result = self.execute_action("continue")
        
        # Remove temporary breakpoint
        if temp_bp and target_line in self.breakpoints:
            self.remove_breakpoint(target_line)
        
        return result


# ============================================
# INTERFACE FOR OTHER TEAMS
# ============================================

def create_debugger_session():
    """
    Factory function for other teams to create debugger sessions.
    
    Usage example:
        from debugger import create_debugger_session
        from tracer import generate_trace
        
        code = '''def add(a, b):
    return a + b

result = add(3, 4)
print(result)'''
        
        trace, output, error = generate_trace(code)
        
        debugger = create_debugger_session()
        debugger.start_session(code, trace)
        
        # Register visualization callback
        def visualize(event, line):
            state = debugger.get_state()
            scope = debugger.get_scope_info(line)
            print(f"{event} at line {line}")
            print(f"  Depth: {state['current_depth']}, Indent: {scope['indent']}")
        
        debugger.register_callback(visualize)
        
        # Step through
        while debugger.is_active:
            result = debugger.execute_action("step")
            print(f"Line {result['next_line']}: {result['current_code']}")
    """
    return DebuggerSession()