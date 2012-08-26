import inspect

from astkit import ast

def get_normalized_source(func):
    source = inspect.getsource(func)
    source_lines = source.splitlines(False)[1:]
    base_indentation = 0
    while source_lines[0][base_indentation] == ' ':
        base_indentation += 1
    normal_source =\
        "\n".join(line[base_indentation:] for line in source_lines)
    return normal_source

def load_module(func):
    normal_source = get_normalized_source(func)
    module = ast.parse(normal_source)
    return module, normal_source

