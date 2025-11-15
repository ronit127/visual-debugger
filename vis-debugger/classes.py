import ast
import warnings
from objects import VariableData, ErrorClass, Operation


class ListTraverser(ast.NodeVisitor):
    def __init__(self):
        super().__init__()

    def which_node(self,node_name):
        for i,item in enumerate(self.list_vars):
            if item.name == node_name:
                return i

    def parse_code(self, code: str) -> list[VariableData]:
        tree = ast.parse(code)
        self.list_vars = list()
        self.visit(tree)

        return self.list_vars

    def get_value(self, node):
        """Return a representation of an AST node's value."""
        if isinstance(node, ast.Constant):
            return repr(node.value)
        elif isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.BinOp):
            return f"({self.get_value(node.left)} {type(node.op).__name__} {self.get_value(node.right)})"
        elif node is None:
            return "None"
        else:
            return ast.unparse(node) if hasattr(ast, "unparse") else str(node)
        
    def do_ds_check(self):
        pass


    def get_visit_Assign_actions(self,node):
        if isinstance(node.value, (ast.List, ast.ListComp)) or (
            isinstance(node.value, ast.Call)
            and isinstance(node.value.func, ast.Name)
            and node.value.func.id == "list"
        ):
            
            for target in node.targets:
                if isinstance(target, ast.Name):
                    new_var = VariableData(
                        name=target.id,
                        var_type="list",
                        operations=[],
                        errors=[]
                    )
                    if new_var not in self.list_vars:
                        self.list_vars.append(new_var)

        elif isinstance(node.value, ast.Name) and node.value.id in self.list_vars:
            for target in node.targets:
                if isinstance(target, ast.Name):
                    new_var = VariableData(
                        name=target.id,
                        var_type="list",
                        operations=[],
                        errors=[]
                    )
                    if new_var not in self.list_vars:
                        self.list_vars.append(new_var)

        for target in node.targets:
            if isinstance(target, ast.Subscript):
                var = target.value
                if isinstance(var, ast.Name):
                    operation = Operation(
                        effect="Set",
                        method=None,
                        line_num=node.lineno,
                        params=[]
                    )
                    self.list_vars[self.which_node(target.value.id)].operations.append(operation)
        
    def visit_Assign(self, node):
        self.get_visit_Assign_actions(node)
        self.do_ds_check()
        self.generic_visit(node)


    def get_visit_Call_actions(self, node):
        if isinstance(node.func, ast.Attribute):
            var = node.func.value
            method = node.func.attr
            if isinstance(var, ast.Name) and var.id in self.list_vars:
                args = [self.get_value(a) for a in node.args]
                operation = Operation()
                if method == "append":
                    operation.effect = "Add"
                    operation.method = "append"
                    operation.index = -1
                elif method == "insert":
                    operation.effect = "Add"
                    operation.method = "insert"
                    operation.index = args[0]
                elif method == "extend":
                    operation.effect = "Add"
                    operation.method = "extend"
                    operation.index = -1
                elif method == "pop":
                    operation.effect = "Remove"
                    operation.method = "pop"
                    operation.index = args[0] if len(args) else -1
                elif method == "count":
                    operation.effect = "InfoRetrieve"
                    operation.method = "count"
                elif method != "copy":
                    operation.effect = "InPlaceMod"
                    operation.method = "unspecified"
                else:
                    operation.effect = "Copy"
                    operation.method = "copy"

                operation.line_num = node.lineno
                operation.params = list() if not len(args) else args[0]
                self.list_vars[self.which_node(var.id)].operations.append(operation)

    def visit_Call(self, node):
        self.get_visit_Call_actions(node)
        self.do_ds_check()
        self.generic_visit(node)

    
    def get_actions(self,node):
        for target in node.targets:
            if isinstance(target, ast.Subscript):
                if isinstance(target.value, ast.Name) and target.value.id in self.list_vars:
                    index = target.slice
                    if isinstance(index, ast.Slice):
                        operation = Operation(
                            effect="Slice",
                            method=None,
                            line_num=node.lineno,
                            params=[index]
                        )
                        self.list_vars[self.which_node(target.id)].operations.append(operation)
                    idx_val = self.get_value(index)
                    if str(idx_val) != "-1":
                        operation = Operation(
                            effect="Delete",
                            method=None,
                            line_num=node.lineno,
                            params=[idx_val],
                            index=idx_val
                        )
                        self.list_vars[self.which_node(target.id)].operations.append(operation)

    def visit_Delete(self,node):
        self.get_actions(node)
        self.do_ds_check()
        self.generic_visit(node)


    def get_AugAssign_checks_actions(self, node):
        if isinstance(node.target, ast.Name):
            var = node.target.id
            if isinstance(node.op, ast.Add):
                rhs = self.get_value(node.value)
                rhs = rhs if type(rhs) == list else [rhs]
                operation = Operation(
                    effect="Add",
                    method=None,
                    line_num=node.lineno,
                    params=[-1],
                    index = -1
                )
                self.list_vars[self.which_node(var)].operations.append(operation)
    
    def visit_AugAssign(self, node):
        self.get_AugAssign_checks_actions(node)
        self.do_ds_check()
        self.generic_visit(node)

class StackTraverser(ListTraverser):
    def __init__(self):
        super().__init__()

    def do_ds_check(self):
        for i,var in enumerate(self.list_vars):
            for action in var.operations:
                error = ErrorClass(
                    name="DS Rule Violation Error",
                    line_num=action.line_num,
                    error_msg=""
                )
                if action.effect == "Add":
                    if action.index != -1:
                        error.error_msg = "Cannot insert into middle of a stack"
                        self.list_vars[i].errors.append(error)
                elif action.effect == "Remove":
                    if action.index != -1:
                        error.error_msg = "Cannot remove from the middle of a stack"
                        self.list_vars[i].errors.append(error)
                elif action.effect == "Slice":
                    error.error_msg = "Slicing not allowed on stack data structures."
                    self.list_vars[i].errors.append(error)
                elif action.effect == "Set":
                    error.error_msg = "Cannot set in a stack"
                    self.list_vars[i].errors.append(error)

#dictTraversing Class
class DictTraverser(ast.NodeVisitor):
    def __init__(self):
        super().__init__()
        self.dict_vars: list[VariableData] = []

    def which_node(self, name):
        for i, item in enumerate(self.dict_vars):
            if item.name == name:
                return i
        return None

    def parse_code(self, code: str) -> list[VariableData]:
        tree = ast.parse(code)
        self.dict_vars = []
        self.visit(tree)
        return self.dict_vars


    def get_value(self, node):
        try:
            return ast.literal_eval(node)
        except Exception:
            if isinstance(node, ast.Constant):
                return node.value
            elif isinstance(node, ast.Name):
                return node.id
            elif hasattr(ast, "unparse"):
                return ast.unparse(node)
            else:
                return str(node)

    def do_ds_check(self):
        """Override this in subclasses (like StackTraverser) to define DS rules."""
        pass

    def visit_Assign(self, node):
        self.handle_assign(node)
        self.do_ds_check()
        self.generic_visit(node)

    def handle_assign(self, node):
        for target in node.targets:
            # Detect new dict creation:  d = {}
            if isinstance(target, ast.Name):
                if isinstance(node.value, ast.Dict):
                    new_var = VariableData(
                        name=target.id,
                        var_type="dict",
                        operations=[],
                        errors=[]
                    )
                    if new_var not in self.dict_vars:
                        self.dict_vars.append(new_var)

            # Detect dict[key] = value
            elif isinstance(target, ast.Subscript) and isinstance(target.value, ast.Name):
                varname = target.value.id
                idx = self.which_node(varname)
                if idx is not None:
                    key = self.get_value(target.slice)
                    value = self.get_value(node.value)

                    op = Operation(
                        effect="Set",
                        method="__setitem__",
                        line_num=node.lineno,
                        params=[key, value],
                        index=key
                    )
                    self.dict_vars[idx].operations.append(op)

    def visit_Delete(self, node):
        self.handle_delete(node)
        self.do_ds_check()
        self.generic_visit(node)

    def handle_delete(self, node):
        for target in node.targets:
            if isinstance(target, ast.Subscript) and isinstance(target.value, ast.Name):
                varname = target.value.id
                idx = self.which_node(varname)
                if idx is not None:
                    key = self.get_value(target.slice)
                    op = Operation(
                        effect="Delete",
                        method="del",
                        line_num=node.lineno,
                        params=[key],
                        index=key
                    )
                    self.dict_vars[idx].operations.append(op)
    def visit_Subscript(self, node):
        self.handle_subscript(node)
        self.do_ds_check()
        self.generic_visit(node)

    def handle_subscript(self, node):
        if isinstance(node.value, ast.Name):
            varname = node.value.id
            idx = self.which_node(varname)
            if idx is not None:
                key = self.get_value(node.slice)
                op = Operation(
                    effect="Read",
                    method="__getitem__",
                    line_num=node.lineno,
                    params=[key],
                    index=key
                )
                self.dict_vars[idx].operations.append(op)

   
    # Method calls: d.get(), d.pop(), d.update()

    def visit_Call(self, node):
        self.handle_call(node)
        self.do_ds_check()
        self.generic_visit(node)

    def handle_call(self, node):
        if not isinstance(node.func, ast.Attribute):
            return

        method = node.func.attr
        var_node = node.func.value

        if not isinstance(var_node, ast.Name):
            return

        varname = var_node.id
        idx = self.which_node(varname)
        if idx is None:
            return

        args = [self.get_value(a) for a in node.args]

        op = Operation(
            effect="",
            method=method,
            line_num=node.lineno,
            params=args
        )


        if method == "get":
            op.effect = "InfoRetrieve"
        elif method == "pop":
            op.effect = "Remove"
            op.index = args[0] if args else None
        elif method == "update":
            op.effect = "InPlaceMod"
        elif method == "clear":
            op.effect = "Clear"
        elif method == "setdefault":
            op.effect = "AddIfMissing"
            op.index = args[0]
        elif method in ("keys", "values", "items"):
            op.effect = "InfoRetrieve"
        else:
            op.effect = "Other"

        self.dict_vars[idx].operations.append(op)


#heapTraverse Class
class HeapTraverser(ast.NodeVisitor):
    def __init__(self):
        super().__init__()
        self.heap_vars: list[VariableData] = []

    def which_node(self, name):
        for i, var in enumerate(self.heap_vars):
            if var.name == name:
                return i
        return None

    def parse_code(self, code: str) -> list[VariableData]:
        tree = ast.parse(code)
        self.heap_vars = []
        self.visit(tree)
        return self.heap_vars

    def get_value(self, node):
        try:
            return ast.literal_eval(node)
        except Exception:
            if isinstance(node, ast.Constant):
                return node.value
            elif isinstance(node, ast.Name):
                return node.id
            elif hasattr(ast, "unparse"):
                return ast.unparse(node)
            return str(node)

    def do_ds_check(self):
        """Override this in subclasses to enforce heap rules."""
        pass


    def visit_Assign(self, node):
        self.handle_assign(node)
        self.do_ds_check()
        self.generic_visit(node)

    def handle_assign(self, node):
        for target in node.targets:

            # Detect: h = []
            if isinstance(target, ast.Name):
                if isinstance(node.value, ast.List) and not node.value.elts:
                    new_var = VariableData(
                        name=target.id,
                        var_type="heap",
                        operations=[],
                        errors=[]
                    )
                    if new_var not in self.heap_vars:
                        self.heap_vars.append(new_var)

            # Detect: heapify(h)
            if isinstance(node.value, ast.Call):
                fn = node.value.func
                if isinstance(fn, ast.Name) and fn.id == "heapify":
                    if node.value.args and isinstance(node.value.args[0], ast.Name):
                        heapname = node.value.args[0].id
                        new_var = VariableData(
                            name=heapname,
                            var_type="heap",
                            operations=[],
                            errors=[]
                        )
                        if new_var not in self.heap_vars:
                            self.heap_vars.append(new_var)

                        idx = self.which_node(heapname)
                        op = Operation(
                            effect="Reorder",
                            method="heapify",
                            line_num=node.lineno,
                            params=[]
                        )
                        self.heap_vars[idx].operations.append(op)


    def visit_Call(self, node):
        self.handle_call(node)
        self.do_ds_check()
        self.generic_visit(node)

    def handle_call(self, node):
        fn = node.func

        # Case 1: direct call e.g. heappush(h, x)
        if isinstance(fn, ast.Name):
            method = fn.id

        # Case 2: attribute call e.g. heapq.heappush
        elif isinstance(fn, ast.Attribute):
            method = fn.attr

        else:
            return

        if method not in {
            "heappush", "heappop", "heapify",
            "heapreplace", "heappushpop"
        }:
            return

        # Need the heap name (first argument)
        if not node.args:
            return
        arg0 = node.args[0]

        if not isinstance(arg0, ast.Name):
            return

        heapname = arg0.id
        idx = self.which_node(heapname)
        if idx is None:
            return

        # Build an Operation
        op = Operation(
            method=method,
            line_num=node.lineno
        )

        if method == "heappush":
            op.effect = "Add"
            if len(node.args) > 1:
                op.params = [self.get_value(node.args[1])]

        elif method == "heappop":
            op.effect = "Remove"
            op.params = []

        elif method == "heapify":
            op.effect = "Reorder"
            op.params = []

        elif method == "heapreplace":
            op.effect = "Replace"
            if len(node.args) > 1:
                op.params = [self.get_value(node.args[1])]

        elif method == "heappushpop":
            op.effect = "AddRemove"
            if len(node.args) > 1:
                op.params = [self.get_value(node.args[1])]

        # Save operation
        self.heap_vars[idx].operations.append(op)


if __name__ == "__main__":
    sample = """
l = [1, 2, 3, 4]
l.append(1)
l.pop()
l.extend([5,6])
# l.insert(0, 99)
# l.remove(2)
l += [7]
l[0] = 100
del l[-1]
a = list()
b = a        # aliasing
b.append(42)
c = a
c.pop()
"""
    stack_traverser = StackTraverser()
    x = stack_traverser.parse_code(sample)
    print(x)
    

class PartialRunner:

    
    def __init__(self, code: str):
        self.code = code
        self.tree = ast.parse(code)

    def partial_run(self, target_line: int):
        
        allowed_nodes = []

        for node in self.tree.body:
            # Only include statements fully starting before or at target_line
            if hasattr(node, "lineno") and node.lineno <= target_line:
                allowed_nodes.append(node)

        partial_module = ast.Module(
            body=allowed_nodes,
            type_ignores=[]
        )

        # Compile that partial AST
        compiled = compile(partial_module, filename="<partial>", mode="exec")

        # Run it in an isolated environment
        env = {}
        exec(compiled, env)

        return env
