import ast
import astor


def replace_node(src_code, target_node, new_code):
    # Parse the source code into an AST
    tree = ast.parse(src_code)

    # Iterate over all nodes in the AST
    for node in ast.walk(tree):
        # Replace the node if its name matches the target
        if (
            isinstance(node, (ast.FunctionDef, ast.ClassDef))
            and node.name == target_node
        ):
            new_tree = ast.parse(new_code)
            if isinstance(new_tree, ast.Module):
                new_node = new_tree.body[0]
                node.name = new_node.name
                node.args = new_node.args
                node.body = new_node.body
                node.decorator_list = new_node.decorator_list
                node.returns = new_node.returns
                break

    # Generate updated source code from the modified AST
    return astor.to_source(tree)
