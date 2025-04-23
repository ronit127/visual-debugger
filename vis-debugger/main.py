from flask import Flask, render_template, request, jsonify
import ast
import networkx as nx

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
        elif action == "step":
            return curr_line+1
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
    return trace_list[i] + 1


def parseGraphs(code):
    #parse graphs with AST
    #identify the variables that contain the data structure
    #isolate functions like add_node and delete_node
    #once detected, call sister functions to change the visualisation

    tree = ast.parse(code)
    graph_variables = set()

    #check for nx.Graph() being called
    for node in ast.walk(tree):
        #if assignment
        if isinstance(node, ast.Assign):
            #node.targets=variables
            for target in node.targets:
                if isinstance(target, ast.Name):
                    #right side = function call and has an attribute = Graph()
                    if isinstance(node.value, ast.Call) and isinstance(node.value.func, ast.Attribute):
                        if node.value.func.attr == "Graph" and isinstance(node.value.func.value, ast.Name):
                            graph_variables.add(target.id)

        #check if it is a function call
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Attribute):
                #name of the function called
                func_name = node.func.attr
                graph_functions = ['add_node', 'add_nodes_from', 'add_edge', 'add_edges_from', 'remove_node', 'remove_nodes_from', 'remove_edge', 'remove_edges_from']
                if func_name in graph_functions:
                    if isinstance(node.func.value, ast.Name):
                        
                        #variable: node.func.value.id,
                        #action: func_name,
                        #arguments: [ast.dump(arg) for arg in node.args]


