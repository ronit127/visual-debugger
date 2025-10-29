from flask import Flask, render_template, request, jsonify
import ast
import networkx as nx
from pymongo import MongoClient
import heapq

app = Flask(__name__)

# Global variable to store graph operations for the current session
graph_operations = []

client = MongoClient('mongodb://localhost:27017/')
db = client['code_storage']
collection = db['users']

@app.route('/add_data', methods=['POST'])
def add_data():
    """Add data to MongoDB collection."""
    data = request.json
    collection.insert_one(data)
    return jsonify({"message": "Data added!"}), 201

@app.route('/get_data', methods=['GET'])
def get_data():
    """Get all data from MongoDB collection, hiding _id."""
    data = list(collection.find({}, {"_id": 0}))  # Hide MongoDB ID
    return jsonify(data)

@app.route('/')
def index():
    """Render the main index page."""
    return render_template('index2.html')

@app.route('/api/run', methods=['POST'])
def run_code():
    """Run code and return output and graph operations."""
    try:
        global graph_operations
        # Reset graph operations for a new run
        graph_operations = []

        data = request.get_json()
        code = data.get('code', '')

        if code.strip() == "":
            return jsonify({'status': 'error', 'error': 'No code provided'})

        # Parse the code for graph operations
        parseGraphs(code)

        #output = f"Processed: {code}"
        # Sample graph data for visualization
        exec_result = execute_code(code)
        print(exec_result['status'])

        graph_data = {
            "nodes": [
                {"id": 1, "label": "1"},
                {"id": 2, "label": "2"},
                {"id": 3, "label": "3"}
            ],
            "links": [
                {"source": 1, "target": 2},
                {"source": 2, "target": 3}
            ]
        }
        return jsonify({
            'status': exec_result['status'],
            'output': exec_result['output'],
            'graph_operations': graph_operations,  # Include graph operations in the response
            'graph': graph_data
        })

    except Exception as e:
        return jsonify({'status': 'error', 'error': str(e)})


import io, contextlib

def execute_code(code):
    """Run code handling and returning output and errors, if any"""
    print("Executing code...")
    output = ""
    status = "success"

    f = io.StringIO()
    try:
        compiled_code = compile(code, "<string>", "exec")
        with contextlib.redirect_stdout(f):
            exec(compiled_code)
        output = f.getvalue()
    except IndentationError as e:
        status = str(e)
    except SyntaxError as e:
        status = str(e)
    except NameError as e:
        status = str(e)
    except Exception as e:
        status = str(e)

    return {
        "status": status,
        "output": output
    }

def choose_next_line(breakpoints, partial_trace):
    """
    Arguments:
        breakpoints: Dict {line_num: "action"} (e.g., {10: "step into"})
        parsed_trace: List of executed line numbers (from parseTrace())
    Returns:
        Next line number to pause at, or None to continue
    """
    if len(partial_trace) == 0:
        return None

    curr_line = partial_trace[-1]

    # Is curr_line a breakpoint?
    if curr_line in breakpoints:
        action = breakpoints[curr_line]
        if action == "continue":
            return None
        elif action == "step":
            return curr_line + 1
        elif action == "step into":
            return next_line_in_function(partial_trace, curr_line)
        elif action == "step over":
            return next_line_after_function(partial_trace, curr_line)
        else:
            return None


def next_line_in_function(trace_list, cl):
    """
    Arguments:
        trace_list : list of line numbers from parse trace
        cl : current line
    """
    if len(trace_list) == 0:
        return None
    return trace_list[trace_list.index(cl) + 1]


def next_line_after_function(trace_list, cl):
    """
    Arguments:
        trace_list : list of line numbers from parse trace
        cl : current line
    """
    if len(trace_list) == 0:
        return None
    i = trace_list.index(cl)
    return trace_list[i] + 1


def parseGraphs(code):
    """Parse code for graph operations using AST."""
    tree = ast.parse(code)
    graph_variables = set()

    # Check for nx.Graph() being called
    for node in ast.walk(tree):
        # If assignment
        if isinstance(node, ast.Assign):
            # node.targets=variables
            for target in node.targets:
                if isinstance(target, ast.Name):
                    # right side = function call and has an attribute = Graph()
                    if isinstance(node.value, ast.Call) and isinstance(node.value.func, ast.Attribute):
                        if node.value.func.attr == "Graph" and isinstance(node.value.func.value, ast.Name):
                            graph_variables.add(target.id)
                            # Log graph creation
                            addGraphCreation(target.id)

        # Check if it is a function call
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Attribute):
                # name of the function called
                func_name = node.func.attr
                graph_functions = [
                    'add_node', 'add_nodes_from', 'add_edge', 'add_edges_from',
                    'remove_node', 'remove_nodes_from', 'remove_edge', 'remove_edges_from'
                ]
                if func_name in graph_functions:
                    if isinstance(node.func.value, ast.Name):
                        graph = node.func.value.id

                        if func_name == 'add_node':
                            try:
                                node_val = ast.literal_eval(node.args[0])
                                addNode(graph, node_val)
                            except Exception:
                                pass

                        elif func_name == 'add_nodes_from':
                            list_nodes = node.args[0]
                            if isinstance(list_nodes, ast.List):
                                for elt in list_nodes.elts:
                                    try:
                                        node_val = ast.literal_eval(elt)
                                        addNode(graph, node_val)
                                    except Exception:
                                        pass

                        elif func_name == 'add_edge':
                            try:
                                node1 = ast.literal_eval(node.args[0])
                                node2 = ast.literal_eval(node.args[1])
                                addEdge(graph, node1, node2)
                            except Exception:
                                pass

                        elif func_name == 'add_edges_from':
                            edge_list = node.args[0]
                            if isinstance(edge_list, ast.List):
                                for edge_ast in edge_list.elts:
                                    if isinstance(edge_ast, ast.Tuple) and len(edge_ast.elts) == 2:
                                        try:
                                            node1 = ast.literal_eval(edge_ast.elts[0])
                                            node2 = ast.literal_eval(edge_ast.elts[1])
                                            addEdge(graph, node1, node2)
                                        except Exception:
                                            pass

                        elif func_name == 'remove_edge':
                            try:
                                node1 = ast.literal_eval(node.args[0])
                                node2 = ast.literal_eval(node.args[1])
                                removeEdge(graph, node1, node2)
                            except Exception:
                                pass

                        elif func_name == 'remove_edges_from':
                            edge_list_ast = node.args[0]
                            if isinstance(edge_list_ast, ast.List):
                                for edge_ast in edge_list_ast.elts:
                                    if isinstance(edge_ast, ast.Tuple) and len(edge_ast.elts) == 2:
                                        try:
                                            node1 = ast.literal_eval(edge_ast.elts[0])
                                            node2 = ast.literal_eval(edge_ast.elts[1])
                                            removeEdge(graph, node1, node2)
                                        except Exception:
                                            pass

                        elif func_name == 'remove_node':
                            try:
                                node_remove = ast.literal_eval(node.args[0])
                                removeNode(graph, node_remove)
                            except Exception:
                                pass

                        elif func_name == 'remove_nodes_from':
                            list_node_remove = node.args[0]
                            if isinstance(list_node_remove, ast.List):
                                for elt in list_node_remove.elts:
                                    try:
                                        node_val = ast.literal_eval(elt)
                                        removeNode(graph, node_val)
                                    except Exception:
                                        pass

def addGraphCreation(graph_name):
    """Log graph creation operation."""
    graph_operations.append(f"Graph created: '{graph_name}'")

def addNode(graph, node):
    """Log node addition operation."""
    graph_operations.append(f"Graph '{graph}': Node added with value: {node}")

def addEdge(graph, node1, node2):
    """Log edge addition operation."""
    graph_operations.append(f"Graph '{graph}': Edge added between {node1} and {node2}")

def removeEdge(graph, node1st, node2nd):
    """Log edge removal operation."""
    graph_operations.append(f"Graph '{graph}': Edge removed between {node1st} and {node2nd}")

def removeNode(graph, node_r):
    """Log node removal operation."""
    graph_operations.append(f"Graph '{graph}': Node removed with value: {node_r}")



c = """
l = [1, 2, 3, 4]
l.append(1)
l.pop()
"""



def list_parse(code: str):
    tree = ast.parse(code)
    list_vars = set()

# walking throuhg ast nodes
# need class for bc ast works with classes that extend NodeVisitor
    class Functions(ast.NodeVisitor):
        #whenever x= is found
        def visit_Assign(self, node):
            # checks if it is a list assignment
            if isinstance(node.value, ast.List):
                # if a list adds the variable names
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        list_vars.add(target.id)
                        for elt in node.value.elts:
                        # call the visualization add
                            print("adding existing element") # call the visualization add
            #self.generic_visit(node) # keep going through the rest of the tree under this node so nothing else gets missed
           


        def visit_Call(self, node):
            # check if method call on variable
            if isinstance(node.func, ast.Attribute) and isinstance(node.func.value, ast.Name):
                var_name = node.func.value.id
                method_name = node.func.attr
                if var_name in list_vars:
                    if method_name == 'append'or method_name == 'push':
                        print("adding a node") # call tje visualization add
                    elif method_name == 'pop':
                        print("deleting a node") # call the visualization delete
            #self.generic_visit(node)
    #visit_assign and visit_call get called automatically by the NodeVisitor
    Functions().visit(tree)


list_parse(c)

heap_operations = []

heap_data = {}

def heapCreation(heap_name):
    heap_data[heap_name] = []
    '''tentative operations logging'''
    heap_operations.append(f"Heap '{heap_name}' created.")

def heapPush(heap_name, value):
    heapq.heappush(heap_data[heap_name], value)
    heap_operations.append(f"Heap '{heap_name}': pushed {value}.")

def heapPop(heap_name):
    if heap_data[heap_name]:
        val = heapq.heappop(heap_data[heap_name])
        heap_operations.append(f"Heap '{heap_name}': popped {val}.")
    else:
        heap_operations.append(f"Heap '{heap_name}': is empty.")
    
def heapify(heap_name):
    heapq.heapify(heap_data[heap_name])
    heap_operations.append(f"Heap '{heap_name}': heapified.")

def heapReplace(heap_name, value):
    if heap_data[heap_name]:
        old = heapq.heapreplace(heap_data[heap_name], value)
        heap_operations.append(f"Heap '{heap_name}': Replace {old} with {value}. ")
    else:
        heap_operations.append(f"Heap '{heap_name}': Cannot Replace.")

def heapPushPop(heap_name, value):
    removed = heapq.heappushpop(heap_data[heap_name], value)
    heap_operations.append(f"Heap '{heap_name}': pushpop {value} (removed {removed}) → {heap_data[heap_name]}.")


def heap_parse(code: str):
    tree = ast.parse(code)
    heap_vars = set()

    class Functions(ast.NodeVisitor):

        def visit_Assign(self, node):
            for target in node.targets:
                if isinstance(target, ast.Name):

                    #detecting the heap
                    if isinstance(node.value, ast.List) and not node.value.elts:
                        heap_vars.add(target.id)
                        heapCreation(target.id)

                
                elif isinstance(node.value, ast.Call):
                        func = node.value.func
                        if isinstance(func, ast.Attribute) or isinstance(func, ast.Name):
                            func_name = func.attr if isinstance(func, ast.Attribute) else func.id
                            if func_name == 'heapify' and node.value.args:
                                arg = node.value.args[0]
                                if isinstance(arg, ast.Name):
                                    heap_vars.add(arg.id)
                                    print(f"Heapified list: {arg.id}")

                    
            self.generic_visit(node)

        def visit_Call(self, node):
            

            func_name = None
            module_name = None

            if isinstance(node.func, ast.Attribute):
                func_name = node.func.attr
                if isinstance(node.func.value, ast.Name):
                    module_name = node.func.value.id
            elif isinstance(node.func, ast.Name):
                func_name = node.func.id


            if func_name in ['heappush', 'heappop', 'heapify', 'heapreplace', 'heappushpop']:
                if node.args and isinstance(node.args[0], ast.Name):
                    heap_name = node.args[0].id

                    if heap_name in heap_vars:                       
                        try:
                            if func_name == 'heappush' and len(node.args) > 1:
                                val = ast.literal_eval(node.args[1])
                                heapPush(heap_name, val)
                            elif func_name == 'heappop':
                                heapPop(heap_name)
                            elif func_name == 'heapify':
                                heapify(heap_name)
                            elif func_name == 'heapreplace' and len(node.args) > 1:
                                val = ast.literal_eval(node.args[1])
                                heapReplace(heap_name, val)
                            elif func_name == 'heappushpop' and len(node.args) > 1:
                                val = ast.literal_eval(node.args[1])
                                heapPushPop(heap_name, val)
                        except Exception as e:
                            print(f"Error processing {func_name}: {e}")

            self.generic_visit(node)
    
    Functions().visit(tree)
    print(heap_operations)

heapsample = """
import heapq

h = []
heapq.heappush(h, 5)
heapq.heappush(h, 1)
heapq.heappop(h)
heapq.heappushpop(h, 10)
heapq.heapreplace(h, 3)
heapq.heapify(h)
"""

heap_parse(heapsample)
