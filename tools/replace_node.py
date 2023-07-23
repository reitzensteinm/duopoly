import ast
import astor


def replace_node(code, node_name, replacement_code):
    tree = astor.parse(code)
    replacement_tree = astor.parse(replacement_code)

    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.ClassDef)) and node.name == node_name:
            node.body = replacement_tree.body
            break
    else:
        raise ValueError(f"No node with name '{node_name}' found in source code.")

    return astor.to_source(tree)
