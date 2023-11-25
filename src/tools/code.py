import ast
import astor


def replace_node(src_code: str, target_node: str, new_code: str) -> str:
    """
    Replace the specified node in the source code with new code.

    The function searches the Abstract Syntax Tree (AST) for the target node. If found, it is replaced with the parsed contents of new_code.

    Args:
            src_code (str): The source code to search.
            target_node (str): The name of the node to replace.
            new_code (str): The new code to insert in place of the old node.

    Returns:
            str: The source code after the replacement has been made.
    """
    node_found = False
    tree = ast.parse(src_code)
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.ClassDef, ast.Assign)) and (
            hasattr(node, "name")
            and node.name == target_node
            or isinstance(node, ast.Assign)
            and isinstance(node.targets[0], ast.Name)
            and node.targets[0].id == target_node
        ):
            node_found = True
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
    if not node_found:
        raise ValueError(
            f"Node '{target_node}' does not exist in the supplied source code."
        )
    return astor.to_source(tree)
