"""
Modify modules by removing attributes
"""

import os
import ast
import sys
import copy
import inspect
import importlib

from pathlib import Path

from ltrim.transformers import RemoveAttribute, SetFix
from ltrim.utils import cp, MAGIC_ATTRIBUTES

DEBUG = False


def tag_members(members):
    """
    Tag attributes as class, function, module or variable
    e.g. (m, <module 'm' from '/path/to/module/m'>) -> (m, 'module')
    """

    def tag(t):
        """
        Tag entries

        :param t: Tuple of (member, value)
        """
        member, val = t
        if inspect.isclass(val):
            return (member, "class")
        if inspect.isfunction(val):
            return (member, "function")
        if inspect.ismodule(val):
            return (member, "module")
        return (member, "variable")

    return list(map(tag, members))


class Moduify:
    """
    Instance of modifier

    :param module_name: Name of the module to modify
    :param marked_attributes: Attributes that must be kept
    """

    def __init__(self, module_name, marked_attributes):

        self.module_name = module_name

        # Load the module
        module = importlib.import_module(module_name)

        # We only need the members that are also in dir(module)
        self.members = module.__dict__

        # Get the path of the module
        try:
            self.module_path = self.members["__file__"]
        except KeyError:
            self.module_path = inspect.getfile(module)

        # Compute set of attributes that cannot be removed
        self.needed_attrs = set(marked_attributes + MAGIC_ATTRIBUTES)

        # Get the complete set of attributes
        self.members = {
            key: value
            for key, value in self.members.items()
            if key in dir(module)
        }

        # Get the basename of the module
        self.basename = os.path.basename(self.module_path)

        # Retrieve the AST of the module or None if it isn't a Python file
        if Path(self.module_path).suffix == ".py":
            self.ast = ast.parse(inspect.getsource(module))
        else:
            self.ast = None

        # Create a backup directory and copy the module to it
        self.backup_dir = os.path.abspath("tmp/" + module_name)
        cp(self.module_path, self.backup_dir + "/" + self.basename)

    def modify(self, attributes: list, remove=False):
        """
        Modify the module by removing the attributes
        """

        if remove:
            members_to_remove = [
                member
                for member in self.members.items()
                if (member[0] in attributes)
                and (member[0] not in self.needed_attributes)
            ]
        else:
            members_to_remove = [
                member
                for member in self.members.items()
                if (member[0] not in attributes)
                and (member[0] not in self.needed_attributes)
            ]

        # logger.info(
        #     "%d attributes to remove: %s",
        #     len(members_to_remove),
        #     [attr[0] for attr in members_to_remove],
        # )

        try:
            cp(self.backup_dir + "/" + self.basename, self.module_path)
        except Exception as e:
            # logger.error("Error copying module source")
            # logger.error(e)
            print(f"Error copying module source: {e}")
            sys.exit(1)

        module_ast = copy.deepcopy(self.ast)

        remove_transformer = RemoveAttribute(tag_members(members_to_remove))
        module_ast = remove_transformer.visit(module_ast)

        # TODO: Find a way to detect modules that require the SetFix transformer
        if self.module_name == "numpy":
            numpyfix = SetFix(members_to_remove)
            module_ast = numpyfix.visit(module_ast)

        if DEBUG:
            print(ast.dump(module_ast, annotate_fields=True, indent=1))

        with open(self.module_path, "w", encoding="utf-8") as out:
            new_source = ast.unparse(module_ast)
            out.write(new_source)
            out.flush()

        return module_ast

    def restore_original_directory(self):
        """
        Move the backup init file back to the original directory
        """

        original_file = self.backup_dir + "/__init__.py"

        if self.module_name not in sys.stdlib_module_names:
            cp(original_file, self.module_path + "/__init__.py")
