import ast
import warnings

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

def find_list_ops(code: str):
    tree = ast.parse(code)
    list_vars = set()

    def get_value(node):
        """Return a representation of an AST node's value."""
        if isinstance(node, ast.Constant):
            return repr(node.value)
        elif isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.BinOp):
            return f"({get_value(node.left)} {type(node.op).__name__} {get_value(node.right)})"
        elif node is None:
            return "None"
        else:
            return ast.unparse(node) if hasattr(ast, "unparse") else str(node)

    class Visitor(ast.NodeVisitor):
        def visit_Assign(self, node):
            if isinstance(node.value, (ast.List, ast.ListComp)) or (
                isinstance(node.value, ast.Call)
                and isinstance(node.value.func, ast.Name)
                and node.value.func.id == "list"
            ):
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        list_vars.add(target.id)
            for target in node.targets:
                if isinstance(target, ast.Subscript):
                    var = target.value
                    if isinstance(var, ast.Name):
                        raise Exception("Cannot set elements in a stack")
            self.generic_visit(node)

        def visit_Call(self, node):
            if isinstance(node.func, ast.Attribute):
                var = node.func.value
                method = node.func.attr
                if isinstance(var, ast.Name) and var.id in list_vars:
                    args = [get_value(a) for a in node.args]

                    if method == "append":
                        print(f"Append of {', '.join(args)} to {var.id}")
                    elif method == "insert":
                        warnings.warn(f"Not best practices on line {node.lineno}, use append and pop for stack data structures.")
                        if len(args) != 2:
                            raise Exception("Incorrect number of params")
                        idx = args[0]
                        item = args[1]
                        if idx != "-1":
                            raise Exception("Cannot insert into middle of a stack")
                        print(f"Inserting {item} at index {idx} in {var.id}")
                    elif method == "pop":
                        if len(args):
                            if len(args) > 1:
                                raise Exception("Incorrect number of params")
                            if args[0] != "-1":
                                raise Exception("Cannot pop from middle of a stack")
                        
                        idx = args[0] if args else "default (end)"
                        print(f"Pop from {var.id}")
                    elif method != "copy":
                        raise Exception("Invalid operation on a stack data structure")
            self.generic_visit(node)

        def visit_Delete(self, node):
            for target in node.targets:
                if isinstance(target, ast.Subscript):
                    if isinstance(target.value, ast.Name) and target.value.id in list_vars:
                        index = target.slice
                        if isinstance(index, ast.Slice):
                            raise Exception("Slicing not allowed on stack data structures.")
                        idx_val = get_value(index)
                        if str(idx_val) != "-1":
                            raise Exception("Cannot delete indices in the middle of a stack data structure")
                        warnings.warn(f"Not best practices on {node.lineno}, use append and pop for stack data structures.")
                        print(f"Pop from {target.value.id}")
            self.generic_visit(node)

        def visit_AugAssign(self, node):
            if isinstance(node.target, ast.Name):
                var = node.target.id
                if isinstance(node.op, ast.Add):
                    warnings.warn(f"Not best practices on {node.lineno}, use append and pop for stack data structures.")
                    rhs = get_value(node.value)
                    print(f"Extending {var} with {rhs}")
            self.generic_visit(node)

    Visitor().visit(tree)


if __name__ == "__main__":
    sample = """
l = [1, 2, 3, 4]
l.append(1)
l.pop()
# l.extend([5,6])
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
    find_list_ops(sample)


# list_parse(c)