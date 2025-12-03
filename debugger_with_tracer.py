from debugger import get_next_line, string_to_lines, create_debugger_session
from tracer import generate_trace, generate_trace_from_file
import os
class InteractiveDebugger:
    """
    Interactive debugger for manual testing.
    Loads tc1.py ... tc10.py automatically.
    """

    def __init__(self, tc_dir="debugger_test_cases"):
        self.debugger = None
        self.loaded_code = None
        self.loaded_trace = None
        self.tc_dir = tc_dir

    def start_interactive_session(self):
        print("\n==============================")
        print("INTERACTIVE DEBUGGER")
        print("==============================")
        print("\nAvailable test case files:\n")

        # List all tc*.py files
        files = sorted(
            f for f in os.listdir(self.tc_dir)
            if f.startswith("tc") and f.endswith(".py")
        )
        sorted_files = []
        for i in range(len(files)):
            sorted_files.append(f"tc{i+1}.py")
            print(f"{i+1}. tc{i+1}.py")
        print(f"\nChoose a test case number (1–{len(files)}), or type 'quit' to exit.")
        choice = input("> ").strip()

        if choice.lower() == "quit":
            print("Exiting debugger.")
            return

        if not choice.isdigit() or not (1 <= int(choice) <= len(files)):
            print("Invalid selection.")
            return

        file_index = int(choice)
        
        filename = sorted_files[file_index-1]
        filepath = os.path.join(self.tc_dir, filename)

        # Load the file
        with open(filepath, "r") as f:
            code = f.read()

        print(f"\nLoaded: {filename}")
        print("----------------------------------")
        print("\nFirst 10 lines of code:")
        print("----------------------------------")

        for i, line in enumerate(code.split("\n")[:10], start=1):
            print(f"{i:3d} | {line}")

        # Generate trace
        print("\nGenerating execution trace...")
        trace, output, error = generate_trace(code)

        if error:
            print("\n❌ Runtime or syntax error detected:")
            print(error)
            return

        print("\n✓ Execution trace generated.")
        print("  First steps:", trace[:20], "..." if len(trace) > 20 else "")

        # Create debugger session
        self.debugger = create_debugger_session()
        self.debugger.start_session(code, trace, breakpoints=[])
        self.loaded_code = code
        self.loaded_trace = trace

        print("\nDebugger ready!")
        print("Commands:")
        print("  step")
        print("  step over")
        print("  step out")
        print("  continue")
        print("  state")
        print("  trace")
        print("  quit\n")

        print("Starting at line:", self.debugger.current_line)

        # Interactive loop
        while True:
            cmd = input("\n> ").strip().lower()

            if cmd == "quit":
                print("Exiting debugger.")
                break

            elif cmd in ("step", "step over", "step out", "continue"):
                self._do_action(cmd)

            elif cmd == "state":
                self.show_state()

            elif cmd == "trace":
                self.show_trace()

            else:
                print("Unknown command. Try: step, step over, step out, continue, state, trace, quit")

    def _do_action(self, action):
        if not self.debugger or not self.debugger.is_active:
            print("Debugger is inactive.")
            return

        result = self.debugger.execute_action(action)

        if result["status"] == "complete":
            print("Program finished.")
            return

        print(f"→ Line {result['next_line']} (depth {result['depth']})")
        print(f"  Code: {result['current_code']}")

    def show_state(self):
        if not self.debugger:
            print("Debugger not started.")
            return

        state = self.debugger.get_state()
        print("\nCurrent Debugger State:")
        for key, val in state.items():
            print(f"  {key}: {val}")

    def show_trace(self):
        if not self.debugger:
            print("Debugger not started.")
            return

        print("\nVisited lines:", self.debugger.execution_history)
if __name__ == "__main__":
    debugger = InteractiveDebugger()
    debugger.start_interactive_session()