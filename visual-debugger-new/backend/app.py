from __future__ import annotations

from flask import Flask, jsonify, render_template, request
from flask_cors import CORS
import ast
import io
import contextlib
import heapq
import os
from typing import Any, Dict, List, Tuple

app = Flask(__name__)
CORS(app)

# ------------------------------
# Graph helpers
# ------------------------------
graph_data: Dict[str, Dict[str, Any]] = {}  # {graph_name: {nodes: {}, links: [], ops: [], next_id: 1}}


def reset_graph_state():
    global graph_data
    graph_data = {}


def ensure_graph(name: str):
    if name not in graph_data:
        graph_data[name] = {
            "nodes": {},
            "links": [],
            "ops": [],
            "next_id": 1,
        }


def add_graph_creation(name: str):
    ensure_graph(name)
    graph_data[name]["ops"].append(f"Graph created: '{name}'")


def add_node(graph: str, node_val: Any):
    ensure_graph(graph)
    g = graph_data[graph]
    if isinstance(node_val, (int, float)):
        node_id = int(node_val)
    else:
        node_id = g["next_id"]
        g["next_id"] += 1
    g["nodes"][node_id] = {"id": node_id, "label": str(node_val)}
    g["ops"].append(f"Graph '{graph}': Node added with value: {node_val}")


def add_edge(graph: str, n1: Any, n2: Any):
    ensure_graph(graph)
    g = graph_data[graph]
    try:
        src = int(n1)
        tgt = int(n2)
    except Exception:
        return
    if src not in g["nodes"]:
        g["nodes"][src] = {"id": src, "label": str(src)}
    if tgt not in g["nodes"]:
        g["nodes"][tgt] = {"id": tgt, "label": str(tgt)}
    g["links"].append({"source": src, "target": tgt})
    g["ops"].append(f"Graph '{graph}': Edge added between {n1} and {n2}")


def remove_node(graph: str, node_val: Any):
    ensure_graph(graph)
    g = graph_data[graph]
    try:
        node_id = int(node_val)
    except Exception:
        return
    g["nodes"].pop(node_id, None)
    g["links"][:] = [l for l in g["links"] if l["source"] != node_id and l["target"] != node_id]
    g["ops"].append(f"Graph '{graph}': Node removed with value: {node_val}")


def remove_edge(graph: str, n1: Any, n2: Any):
    ensure_graph(graph)
    g = graph_data[graph]
    try:
        src = int(n1)
        tgt = int(n2)
    except Exception:
        return
    before = len(g["links"])
    g["links"][:] = [l for l in g["links"] if not (l["source"] == src and l["target"] == tgt)]
    if len(g["links"]) != before:
        g["ops"].append(f"Graph '{graph}': Edge removed between {n1} and {n2}")


def parse_graphs(code: str):
    reset_graph_state()
    tree = ast.parse(code)
    graph_vars = set()

    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    if isinstance(node.value, ast.Call) and isinstance(node.value.func, ast.Attribute):
                        if node.value.func.attr == "Graph" and isinstance(node.value.func.value, ast.Name):
                            graph_vars.add(target.id)
                            add_graph_creation(target.id)

        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
            func_name = node.func.attr
            graph_functions = {
                "add_node",
                "add_nodes_from",
                "add_edge",
                "add_edges_from",
                "remove_node",
                "remove_nodes_from",
                "remove_edge",
                "remove_edges_from",
            }
            if func_name not in graph_functions:
                continue
            if not isinstance(node.func.value, ast.Name):
                continue
            graph = node.func.value.id

            if func_name == "add_node" and node.args:
                try:
                    node_val = ast.literal_eval(node.args[0])
                    add_node(graph, node_val)
                except Exception:
                    pass

            elif func_name == "add_nodes_from" and node.args:
                list_nodes = node.args[0]
                if isinstance(list_nodes, ast.List):
                    for elt in list_nodes.elts:
                        try:
                            node_val = ast.literal_eval(elt)
                            add_node(graph, node_val)
                        except Exception:
                            pass

            elif func_name == "add_edge" and len(node.args) >= 2:
                try:
                    n1 = ast.literal_eval(node.args[0])
                    n2 = ast.literal_eval(node.args[1])
                    add_edge(graph, n1, n2)
                except Exception:
                    pass

            elif func_name == "add_edges_from" and node.args:
                edge_list = node.args[0]
                if isinstance(edge_list, ast.List):
                    for edge_ast in edge_list.elts:
                        if isinstance(edge_ast, ast.Tuple) and len(edge_ast.elts) == 2:
                            try:
                                n1 = ast.literal_eval(edge_ast.elts[0])
                                n2 = ast.literal_eval(edge_ast.elts[1])
                                add_edge(graph, n1, n2)
                            except Exception:
                                pass

            elif func_name == "remove_edge" and len(node.args) >= 2:
                try:
                    n1 = ast.literal_eval(node.args[0])
                    n2 = ast.literal_eval(node.args[1])
                    remove_edge(graph, n1, n2)
                except Exception:
                    pass

            elif func_name == "remove_edges_from" and node.args:
                edge_list = node.args[0]
                if isinstance(edge_list, ast.List):
                    for edge_ast in edge_list.elts:
                        if isinstance(edge_ast, ast.Tuple) and len(edge_ast.elts) == 2:
                            try:
                                n1 = ast.literal_eval(edge_ast.elts[0])
                                n2 = ast.literal_eval(edge_ast.elts[1])
                                remove_edge(graph, n1, n2)
                            except Exception:
                                pass

            elif func_name == "remove_node" and node.args:
                try:
                    n = ast.literal_eval(node.args[0])
                    remove_node(graph, n)
                except Exception:
                    pass

            elif func_name == "remove_nodes_from" and node.args:
                list_nodes = node.args[0]
                if isinstance(list_nodes, ast.List):
                    for elt in list_nodes.elts:
                        try:
                            n = ast.literal_eval(elt)
                            remove_node(graph, n)
                        except Exception:
                            pass


# ------------------------------
# Heap helpers
# ------------------------------
heap_ops: List[str] = []
heap_data: Dict[str, List[Any]] = {}


def reset_heap_state():
    heap_ops.clear()
    heap_data.clear()


def heap_parse(code: str):
    reset_heap_state()
    tree = ast.parse(code)
    heap_vars = set()

    class Visitor(ast.NodeVisitor):
        def visit_Assign(self, node):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    if isinstance(node.value, ast.List) and not node.value.elts:
                        heap_vars.add(target.id)
                        heap_data[target.id] = []
                        heap_ops.append(f"Heap '{target.id}' created.")
            self.generic_visit(node)

        def visit_Call(self, node):
            func_name = None
            if isinstance(node.func, ast.Attribute):
                func_name = node.func.attr
            elif isinstance(node.func, ast.Name):
                func_name = node.func.id
            if func_name not in {"heappush", "heappop", "heapify", "heapreplace", "heappushpop"}:
                return
            if not node.args or not isinstance(node.args[0], ast.Name):
                return
            heap_name = node.args[0].id
            if heap_name not in heap_vars:
                return
            if heap_name not in heap_data:
                heap_data[heap_name] = []
            try:
                if func_name == "heappush" and len(node.args) > 1:
                    val = ast.literal_eval(node.args[1])
                    heapq.heappush(heap_data[heap_name], val)
                    heap_ops.append(f"Heap '{heap_name}': pushed {val}.")
                elif func_name == "heappop":
                    if heap_data[heap_name]:
                        val = heapq.heappop(heap_data[heap_name])
                        heap_ops.append(f"Heap '{heap_name}': popped {val}.")
                    else:
                        heap_ops.append(f"Heap '{heap_name}': is empty.")
                elif func_name == "heapify":
                    heapq.heapify(heap_data[heap_name])
                    heap_ops.append(f"Heap '{heap_name}': heapified.")
                elif func_name == "heapreplace" and len(node.args) > 1:
                    val = ast.literal_eval(node.args[1])
                    if heap_data[heap_name]:
                        old = heapq.heapreplace(heap_data[heap_name], val)
                        heap_ops.append(f"Heap '{heap_name}': replace {old} with {val}.")
                    else:
                        heap_ops.append(f"Heap '{heap_name}': cannot replace on empty heap.")
                elif func_name == "heappushpop" and len(node.args) > 1:
                    val = ast.literal_eval(node.args[1])
                    removed = heapq.heappushpop(heap_data[heap_name], val)
                    heap_ops.append(
                        f"Heap '{heap_name}': pushpop {val} (removed {removed}) → {heap_data[heap_name]}."
                    )
            except Exception as exc:  # best-effort logging
                heap_ops.append(f"Heap '{heap_name}': error processing {func_name}: {exc}")
            self.generic_visit(node)

    Visitor().visit(tree)


# ------------------------------
# List helpers (simple stack-like tracking)
# ------------------------------
list_ops: Dict[str, List[str]] = {}
list_data: Dict[str, List[Any]] = {}


def reset_list_state():
    list_ops.clear()
    list_data.clear()


def list_parse(code: str):
    reset_list_state()
    tree = ast.parse(code)
    list_vars = set()

    class Visitor(ast.NodeVisitor):
        def visit_Assign(self, node):
            if isinstance(node.value, ast.List):
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        name = target.id
                        list_vars.add(name)
                        list_data[name] = [ast.literal_eval(elt) for elt in node.value.elts]
                        list_ops[name] = [f"Initialized with {list_data[name]}"]
            self.generic_visit(node)

        def visit_Call(self, node):
            if isinstance(node.func, ast.Attribute) and isinstance(node.func.value, ast.Name):
                var = node.func.value.id
                method = node.func.attr
                if var in list_vars:
                    ops = list_ops.setdefault(var, [])
                    try:
                        if method == "append" and node.args:
                            val = ast.literal_eval(node.args[0])
                            list_data[var].append(val)
                            ops.append(f"append({val})")
                        elif method == "pop":
                            if list_data[var]:
                                val = list_data[var].pop()
                                ops.append(f"pop() -> {val}")
                            else:
                                ops.append("pop() on empty list")
                    except Exception:
                        ops.append(f"{method}(...) (unresolved)")
            self.generic_visit(node)

    Visitor().visit(tree)


# ------------------------------
# Dict helpers (basic literal + item tracking)
# ------------------------------
dict_ops: Dict[str, List[str]] = {}
dict_data: Dict[str, Dict[Any, Any]] = {}


def reset_dict_state():
    dict_ops.clear()
    dict_data.clear()


def dict_parse(code: str):
    reset_dict_state()
    tree = ast.parse(code)
    dict_vars = set()

    class Visitor(ast.NodeVisitor):
        def visit_Assign(self, node):
            # d = {"a":1}
            if isinstance(node.value, ast.Dict):
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        name = target.id
                        dict_vars.add(name)
                        dict_data[name] = {self._get_key(k): self._get_val(v) for k, v in zip(node.value.keys, node.value.values)}
                        dict_ops[name] = ["initialized"]
            # d[key] = value
            for target in node.targets:
                if isinstance(target, ast.Subscript) and isinstance(target.value, ast.Name):
                    name = target.value.id
                    if name in dict_vars:
                        key = self._get_key(target.slice)
                        value = self._get_val(node.value)
                        dict_data[name][key] = value
                        dict_ops.setdefault(name, []).append(f"set[{key}]={value}")
            self.generic_visit(node)

        def visit_Call(self, node):
            if not (isinstance(node.func, ast.Attribute) and isinstance(node.func.value, ast.Name)):
                return
            name = node.func.value.id
            method = node.func.attr
            if name not in dict_vars:
                return
            ops = dict_ops.setdefault(name, [])
            if method == "pop" and node.args:
                key = self._get_val(node.args[0])
                dict_data[name].pop(key, None)
                ops.append(f"pop({key})")
            elif method == "get" and node.args:
                key = self._get_val(node.args[0])
                ops.append(f"get({key})")
            elif method == "update" and node.args:
                try:
                    payload = self._get_val(node.args[0])
                    if isinstance(payload, dict):
                        dict_data[name].update(payload)
                        ops.append(f"update({payload})")
                except Exception:
                    ops.append("update(...)")
            self.generic_visit(node)

        def _get_key(self, node):
            try:
                return ast.literal_eval(node)
            except Exception:
                return getattr(node, "id", str(node))

        def _get_val(self, node):
            try:
                return ast.literal_eval(node)
            except Exception:
                if isinstance(node, ast.Name):
                    return node.id
                if hasattr(ast, "unparse"):
                    return ast.unparse(node)
                return str(node)

    Visitor().visit(tree)


# ------------------------------
# Execution helper
# ------------------------------

def execute_code(code: str):
    output = ""
    status = "success"
    f = io.StringIO()
    try:
        compiled = compile(code, "<string>", "exec")
        with contextlib.redirect_stdout(f):
            exec(compiled, {})
        output = f.getvalue()
    except Exception as exc:
        status = str(exc)
    return {"status": status, "output": output}


# ------------------------------
# Routes
# ------------------------------

@app.route("/")
def index():
    return "Backend up. Use POST /api/run"


@app.route("/api/run", methods=["POST"])
def run_code():
    try:
        payload = request.get_json(force=True) or {}
        code = payload.get("code", "")
        if not isinstance(code, str) or not code.strip():
            return jsonify({"status": "error", "error": "No code provided"}), 400

        # Parse structures
        parse_graphs(code)
        heap_parse(code)
        list_parse(code)
        dict_parse(code)

        # Execute code
        exec_result = execute_code(code)

        structures = []
        for graph_name, g in graph_data.items():
            if g["nodes"] or g["links"]:
                structures.append({
                    "name": graph_name,
                    "type": "graph",
                    "payload": {
                        "nodes": list(g["nodes"].values()),
                        "links": g["links"],
                    },
                    "operations": g["ops"],
                })
        for name, values in list_data.items():
            structures.append({
                "name": name,
                "type": "list",
                "payload": values,
                "operations": list_ops.get(name, []),
            })
        for name, values in heap_data.items():
            structures.append({
                "name": name,
                "type": "heap",
                "payload": values,
                "operations": heap_ops,
            })
        for name, d in dict_data.items():
            structures.append({
                "name": name,
                "type": "dict",
                "payload": d,
                "operations": dict_ops.get(name, []),
            })

        response = {
            "status": exec_result["status"],
            "output": exec_result["output"],
            "structures": structures,
        }
        return jsonify(response)
    except Exception as exc:
        return jsonify({"status": "error", "error": str(exc)}), 500


@app.route("/health")
def health():
    return {"ok": True}


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "5000"))
    app.run(host="0.0.0.0", port=port, debug=True)
