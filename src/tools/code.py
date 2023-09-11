import ast
import astor


def replace_node(src_code, target_node, new_code):
    # Parse the source code into an AST
    tree = ast.parse(src_code)

    # Iterate over all nodes in the AST
    for node in ast.walk(tree):
        # Replace the node if its name matches the target
        if isinstance(node, (ast.FunctionDef, ast.ClassDef, ast.Assign)) and (
            (hasattr(node, "name") and node.name == target_node)
            or (
                isinstance(node, ast.Assign)
                and isinstance(node.targets[0], ast.Name)
                and node.targets[0].id == target_node
            )
        ):
            new_tree = ast.parse(new_code)
            new_node = new_tree.body[0]

            if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
                node.name = new_node.name
                if isinstance(new_node, (ast.FunctionDef, ast.ClassDef)):
                    node.args = new_node.args
                    node.body = new_node.body
                    node.decorator_list = new_node.decorator_list
                    node.returns = new_node.returns
            elif isinstance(node, ast.Assign):
                if isinstance(new_node, ast.Assign):
                    node.targets[0].id = new_node.targets[0].id
                    node.value = new_node.value

    # Generate updated source code from the modified AST
    return astor.to_source(tree)
