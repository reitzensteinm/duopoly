import ast
import astor
from src.utils import format_code


def to_ast(source: str):
    """Parse Python source into an Abstract Syntax Tree (AST)"""
    return ast.parse(source)


def to_source(tree: ast.AST) -> str:
    """Convert an AST into Python source"""
    return format_code(astor.to_source(tree))
