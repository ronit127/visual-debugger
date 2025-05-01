import ast

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
            ############ to do: check all the other elements of the list when a list is initialized, and call add node on every single one for the visualization
            ########## to do: push/append, pop - quack


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




