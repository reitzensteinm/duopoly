import ast
import astor


def replace_node(src_code, target_node, new_code):
    tree = ast.parse(src_code)
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.ClassDef, ast.Assign)) and (
            hasattr(node, "name")
            and node.name == target_node
            or isinstance(node, ast.Assign)
            and isinstance(node.targets[0], ast.Name)
            and node.targets[0].id == target_node
        ):
            new_tree = ast.parse(new_code)
            new_node = new_tree.body[0]
            if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
                node.name = new_node.name
                if isinstance(new_node, ast.FunctionDef):
                    node.args = new_node.args
                    node.body = new_node.body
                    node.decorator_list = new_node.decorator_list
                    node.returns = new_node.returns
                elif isinstance(new_node, ast.ClassDef):
                    node.bases = new_node.bases
                    node.keywords = new_node.keywords
                    node.body = new_node.body
                    node.decorator_list = new_node.decorator_list
            elif isinstance(node, ast.Assign):
                if isinstance(new_node, ast.Assign):
                    node.targets[0].id = new_node.targets[0].id
                    node.value = new_node.value
    return astor.to_source(tree)
