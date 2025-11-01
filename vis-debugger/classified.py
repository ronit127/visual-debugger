import ast
import warnings


class ListTraverser(ast.NodeVisitor):
    def __init__(self):
        super().__init__()

    def parse_code(self,code):
        self.visit_Assign_actions = list()
        self.visit_Delete_actions = list()
        self.visit_AugAssign_actions = list()

        tree = ast.parse(code)
        self.list_vars = set()
        self.visit(tree)

    def get_value(self,node):
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
        

    def get_visit_Assign_actions(self,node):
        if isinstance(node.value, (ast.List, ast.ListComp)) or (
            isinstance(node.value, ast.Call)
            and isinstance(node.value.func, ast.Name)
            and node.value.func.id == "list"
        ):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    self.list_vars.add(target.id)

        elif isinstance(node.value, ast.Name) and node.value.id in self.list_vars:
            for target in node.targets:
                if isinstance(target, ast.Name):
                    self.list_vars.add(target.id)
    
    def visit_Assign_checks(self):
        pass
        
    def visit_Assign(self, node):
        self.get_visit_Assign_actions(node)
        self.visit_Assign_checks(node)
        self.generic_visit(node)


    def get_visit_Call_actions(self, node):
        if isinstance(node.func, ast.Attribute):
            var = node.func.value
            method = node.func.attr
            if isinstance(var, ast.Name) and var.id in self.list_vars:
                args = [self.get_value(a) for a in node.args]
                if method == "append":
                    self.visit_Assign_actions.append(["Add",-1,[args[0]],var.id])
                elif method == "insert":
                    idx = args[0]
                    item = args[1]
                    self.visit_Assign_actions.append(["Add",idx,[item],var.id])
                elif method == "extend":
                    self.visit_Assign_actions.append(["Add",-1,args[0],var.id])
                elif method == "pop":
                    idx = -1 if not len(args) else args[0]
                    self.visit_Assign_actions.append(["Remove",idx,var.id])
                elif method == "count":
                    self.visit_Assign_actions.append(["InfoRetrive",var.id])
                elif method != "copy":
                    self.visit_Assign_actions.append(["InPlaceMod",var.id])
                else:
                    self.visit_Assign_actions.append(["Copy",var.id])
    
    def visit_Call_checks(self):
        pass

    def visit_Call(self, node):
        self.get_visit_Call_actions(node)
        self.visit_Call_checks()
        self.generic_visit(node)

    
    def get_visit_Delete_actions(self,node):
        for target in node.targets:
            if isinstance(target, ast.Subscript):
                if isinstance(target.value, ast.Name) and target.value.id in self.list_vars:
                    index = target.slice
                    if isinstance(index, ast.Slice):
                        self.visit_Delete_actions.append(["Slice",index])
                    idx_val = self.get_value(index)
                    if str(idx_val) != "-1":
                        self.visit_Delete_actions.append(["Delete",idx_val])

    def visit_Delete_checks(self):
        pass

    def visit_Delete(self,node):
        self.get_visit_Delete_actions(node)
        self.visit_Delete_checks()
        self.generic_visit(node)


    def get_visit_AugAssign_actions(self, node):
        if isinstance(node.target, ast.Name):
            var = node.target.id
            if isinstance(node.op, ast.Add):
                rhs = self.get_value(node.value)
                rhs = rhs if type(rhs) == list else [rhs]
                self.visit_AugAssign_actions.append(["Add",-1, rhs,var])

    def visit_AugAssign_checks(self):
        pass
    
    def visit_AugAssign(self, node):
        self.get_visit_AugAssign_actions(node)
        self.visit_AugAssign_checks()
        self.generic_visit(node)

class StackTraverser(ListTraverser):
    def __init__(self):
        super().__init__()

    def visit_Assign_checks(self,node):
        for target in node.targets:
            if isinstance(target, ast.Subscript):
                var = target.value
                if isinstance(var, ast.Name):
                    raise Exception("Cannot set elements in a stack")

    def visit_Call_checks(self):
        for action in self.visit_Assign_actions:
            if action[0] == "Add":
                if action[1] != -1:
                    raise Exception("Cannot insert into middle of a stack")
            elif action[0] == "Remove":
                if action[1] != -1:
                    raise Exception("Cannot remove from the middle of a stack")
                
    def visit_Delete_checks(self):
        for action in self.visit_Delete_actions:
            if action[0] == "Slice":
                raise Exception("Slicing not allowed on stack data structures.")
            elif action[0] == "Remove":
                warnings.warn("Not best practices, use append and pop for stack data structures.")
                if action[1] != -1:
                    raise Exception("Cannot delete indices in the middle of a stack data structure")

    def visit_AugAssign_checks(self):
        for action in self.visit_AugAssign_actions:
            if action[0] != "Add":
                raise Exception("Can only add to stack")


if __name__ == "__main__":
    sample = """
l = [1, 2, 3, 4]
l.append(1)
l.pop()
l.extend([5,6])
# l.insert(0, 99)
# l.remove(2)
l += [7]
# l[0] = 100
del l[-1]
a = list()
b = a        # aliasing
b.append(42)
c = a
c.pop()
"""
    stack_traverser = StackTraverser()
    stack_traverser.parse_code(sample)
    


# list_parse(c)