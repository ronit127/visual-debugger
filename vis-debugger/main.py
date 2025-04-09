from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index2.html')

@app.route('/api/run', methods=['POST'])
def run_code():
    try:
        data = request.get_json()
        code = data.get('code', '')

        
        if code.strip() == "":
            return jsonify({'status': 'error', 'error': 'No code provided'})

        output = f"Processed: {code}"
        return jsonify({'status': 'success', 'output': output})

    except Exception as e:
        return jsonify({'status': 'error', 'error': str(e)})


def choose_next_line(breakpoints, partial_trace):
    """Arguments:
    breakpoints: Dict {line_num: "action"} (e.g., {10: "step into"})
    parsed_trace: List of executed line numbers (from parseTrace())
    
    Returns:
        Next line number to pause at, or None to continue
    """

    """Add step and stop"""
    if len(partial_trace)==0:
        return None

    curr_line = partial_trace[-1]
    
    # Is curr_line a breakpoint?
    if curr_line in breakpoints:
        action = breakpoints[curr_line]
        if action == "continue":
            return None
        elif action == "step into":
            return next_line_in_function(partial_trace, curr_line)
        elif action == "step over":
            return next_line_after_function(partial_trace,curr_line)
        else:
            return None
    

def next_line_in_function(trace_list,cl):
    """Arguments:
    trace_list : list of line numbers from parse trace
    cl : current line"""
    if len(trace_list)==0:
        return None
    return trace_list[trace_list.index(cl)+1]

def next_line_after_function(trace_list,cl):
    """Arguments:
    trace_list : list of line numbers from parse trace
    cl : current line"""
    if len(trace_list)==0:
        return None
    i=trace_list.index(cl)
    if i+1<len(trace_list):
        return trace_list[i + 1]


