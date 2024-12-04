import argparse
import ast

from ltrim.debloat.process import run_pycg
from ltrim.debloat.utils import blacklist
from ltrim.transformers import ImportsFinder


def main():

    parser = argparse.ArgumentParser(
        prog="Debloat a Python package",
        description="""Debloat a Python application by removing unused
        attributes of imported modules.""",
        epilog="""Developed and maintained by Spyros Pavlatos. Originally created
        in the Distributed Systems Laboratory of University of Pennsylvania""",
    )

    parser.add_argument("filename", type=str, help="Name of the application")

    parser.add_argument(
        "-k", "--top-K", default=10, help="Number of modules to debloat."
    )

    parser.add_argument(
        "-s",
        "--scoring",
        default="cost",
        choices=["cost", "time", "memory", "random"],
        help="The scoring method to calculate the top K ranking of the modules.",
    )

    args = parser.parse_args()

    appname = args.filename

    with open(appname, "r") as f:
        source = f.read()

    ast_source = ast.parse(source)

    # --------------------------------------------------------------------- #
    # ----------------------- Static Analysis Phase ----------------------- #
    # --------------------------------------------------------------------- #

    # Step 1: Find imported modules
    imports_finder = ImportsFinder()
    imports_finder.visit(ast_source)

    # Step 2: Use PyCG to extract the call graph of the application
    call_graph = run_pycg(appname)
    print(call_graph)

    # --------------------------------------------------------------------- #
    # ------------------------ Constructing Phase ------------------------- #
    # --------------------------------------------------------------------- #
    imported_modules = []

    for module_name in imports_finder.imports:

        if module_name in blacklist:
            continue

        imported_modules.append(module_name)

    print(imported_modules)
    # TODO: Check if there are duplicates in the imported modules

    # --------------------------------------------------------------------- #
    # ------------------------- Profiling Phase --------------------------- #
    # --------------------------------------------------------------------- #
