import ast
import sys
from ltrim.transformers.utils import retrieve_name


class ImportsFinder(ast.NodeVisitor):
    """
    Find all import statements in a Python module
    """

    def __init__(self):
        ast.NodeVisitor.__init__(self)
        self.imports = []

    def visit_Import(self, node):
        """
        Custom visit_Import
        """
        self.imports.extend(
            ("Import", (n.name, n.asname))
            for n in node.names
            if n.name not in sys.builtin_module_names
        )
        ast.NodeVisitor.generic_visit(self, node)

    def visit_ImportFrom(self, node):
        """
        Custom visit_ImportFrom
        """
        self.imports.extend(
            ("ImportFrom", (node.module, n.name, n.asname, node.level))
            for n in node.names
            if n.name not in sys.builtin_module_names
        )
        ast.NodeVisitor.generic_visit(self, node)


class RemoveAttribute(ast.NodeTransformer):
    """
    Remove attributes from a Python module

    :param attributes: A list of attributes to remove
    """

    def __init__(self, attributes):
        self.attributes = dict(attributes)

    def visit_Assign(self, node):
        """
        Custom visit_Assign
        """

        newnode = node
        if isinstance(node.value, ast.Call):
            s = retrieve_name(node.value.func)
            if s in self.attributes:
                return ast.Pass()

        first_target = node.targets[0]
        if isinstance(first_target, ast.Name) and (
            first_target.id == "__all__"
        ):
            new_elements = []
            if not hasattr(node.value, "elts"):
                return node
            for element in node.value.elts:
                if retrieve_name(element) in self.attributes:
                    continue
                new_elements.append(element)
            node.value.elts = new_elements

        for target in node.targets:
            if isinstance(target, ast.Name) and target.id in self.attributes:
                if self.attributes[target.id] == "variable":
                    newnode = ast.Pass()

        return newnode

    def visit_FunctionDef(self, node):
        """
        Custom visit_FunctionDef
        """
        if node.name in self.attributes:
            if self.attributes[node.name] == "function":
                return ast.Pass()
        return node

    def visit_ClassDef(self, node):
        """
        Custom visit_ClassDef
        """
        if node.name in self.attributes:
            if self.attributes[node.name] == "class":
                return ast.Pass()
        return node

    def visit_Import(self, node):
        """
        Custom visit_Import
        """
        newnames = []

        for alias in node.names:
            if alias.asname is not None:
                if alias.asname not in self.attributes:
                    newnames.append(alias)
            else:
                if alias.name not in self.attributes:
                    newnames.append(alias)

        if len(newnames) == 0:
            return ast.Pass()

        node.names = newnames

        return node

    def visit_ImportFrom(self, node):
        """
        Custom visit_ImportFrom
        """
        newnames = []

        for alias in node.names:
            if alias.asname is not None:
                if alias.asname not in self.attributes:
                    newnames.append(alias)
            else:
                if alias.name not in self.attributes:
                    newnames.append(alias)

        if len(newnames) == 0:
            return ast.Pass()

        node.names = newnames

        return node


class SetFix(ast.NodeTransformer):
    """
    Fix modules with __all__ = list(set(...)) pattern
    """

    def __init__(self, attributes):
        self.attributes = attributes
        self.fix_lock = False

    def visit_Assign(self, node):
        """
        Custom visit_Assign
        """
        target = node.targets[0]

        if isinstance(target, ast.Name) and target.id == "__all__":
            if isinstance(node.value, ast.Call):
                if isinstance(node.value.func, ast.Name):
                    if node.value.func.id == "list":
                        self.fix_lock = True

        self.generic_visit(node)
        self.fix_lock = False

        return node

    def visit_Call(self, node):
        """
        Custom visit_Call
        """
        if self.fix_lock:
            if isinstance(node.func, ast.Name) and node.func.id == "set":
                new_elements = []
                for element in node.args:
                    c1 = isinstance(element, ast.Attribute)
                    name = retrieve_name(element.value)
                    name = name.split(".")[0] if "." in name else name
                    c3 = name in self.attributes
                    if c1 and c3:
                        continue
                    new_elements.append(element)
                node.args = new_elements
            else:
                self.generic_visit(node)
        else:
            self.generic_visit(node)

        return node
