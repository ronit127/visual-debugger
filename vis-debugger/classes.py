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
    


# list_parse(c)