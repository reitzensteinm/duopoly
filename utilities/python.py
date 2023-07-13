import astor


def parse_to_ast(source_code):
    return astor.code_to_ast.parse(source_code)


def ast_to_source(ast_obj):
    return astor.to_source(ast_obj)
