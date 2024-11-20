import ast


def retrieve_name(node):
    """
    Retrieve the name of a node.
    """
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        value_name = retrieve_name(node.value)
        ret = node.attr
        if value_name is not None:
            ret = value_name + "." + node.attr
        return ret
    if isinstance(node, ast.Call):
        return retrieve_name(node.func)
    if isinstance(node, ast.JoinedStr):
        joined = ""
        for val in node.values:
            if isinstance(val, ast.FormattedValue):
                joined += retrieve_name(val.value)
            elif isinstance(val, ast.Constant):
                joined += val.value
        return joined
    if isinstance(node, ast.Constant):
        return node.value
    return None


def add_tag(entries, tag):
    """
    Mark entries with USED or NOT_USED tags.
    """
    return map(lambda entry: (entry[0], (entry[1], tag)), entries)
