import ast 

code = """
import networkx as nx

G = nx.DiGraph()

G.add_node(1, label = "node1")
G.add_node(2, label = "node2")
G.add_edge(1,2)
"""

tree = ast.parse(code)

with open('ast_output.txt', 'w') as f:
    for node in ast.walk(tree):
        f.write(f"Node type: {type(node)}\n")
        f.write(f"{ast.dump(node, annotate_fields=True)}\n\n")
