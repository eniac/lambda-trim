import argparse
import ast
import logging
from pprint import pformat as pp

from ltrim.debloat.process import debloat, run_profiler, run_pycg

# TODO: from ltrim.debloat.stats import ModuleRecord
from ltrim.debloat.utils import (
    blacklist,
    filter_pycg,
    sort_report,
    update_alive_modules,
)
from ltrim.transformers import ImportsFinder

logger = logging.getLogger(__name__)
logging.basicConfig(
    filename="log/debloat.log",
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)


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
        "-k", "--top-K", type=int, default=10, help="Number of modules to debloat."
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
    print("Finding imports...")
    imports_finder = ImportsFinder()
    imports_finder.visit(ast_source)
    print("Imports found!")
    logger.info(f"Imports found: {imports_finder.imports}")

    # Step 2: Use PyCG to extract the call graph of the application
    print("Extracting call graph...")
    call_graph = run_pycg(appname)
    print("Call graph extracted!")
    logger.info(f"Call graph extracted: {call_graph}")

    # --------------------------------------------------------------------- #
    # ------------------------ Constructing Phase ------------------------- #
    # --------------------------------------------------------------------- #

    # Step 3: Construct a list of the imported modules
    imported_modules = []

    for module_name in imports_finder.imports:

        if module_name in blacklist:
            continue

        imported_modules.append(module_name)

    logger.info(f"Filtered imports: {imported_modules}")

    # TODO: Check if there are duplicates in the imported modules

    # --------------------------------------------------------------------- #
    # ------------------------- Profiling Phase --------------------------- #
    # --------------------------------------------------------------------- #

    # Step 4: Profile the import process of the application
    print("Profiling the import process...")
    report = run_profiler(imported_modules)

    # Extract the total memory used by the imported modules
    total_memory = report["total_memory"]
    del report["total_memory"]

    # Extract the total time taken to import modules
    total_time = sum(
        [report[module]["time"] for module in imported_modules if module in report]
    )

    print(f"Total memory used in the import process: {total_memory:.2f}MB")
    print(f"Total time taken for the import process: {total_time:.2f}ms")

    # Step 5 - Sort the profiler report using the scoring method
    sorted_report = sort_report(report, args.scoring, total_time, total_memory)

    # Filter modules in the blacklist
    sorted_report = [module for module in sorted_report if module[0] not in blacklist]
    logger.info(pp(sorted_report[: args.top_K]))
    print("Profiling completed!")

    # --------------------------------------------------------------------- #
    # ------------------------- Debloating Phase -------------------------- #
    # --------------------------------------------------------------------- #

    # Step 6 - Debloat the top K modules
    modules_to_debloat = [module[0] for module in sorted_report[: args.top_K]]

    alive_modules = set(modules_to_debloat)

    for midx, module in enumerate(modules_to_debloat):

        print(f"Debloating module {module} ({midx + 1}/{args.top_K})")

        if module not in alive_modules:
            print(f"Module {module} is not longer needed!")
            continue

        # Step 6.1 - Filter the PyCG attributes
        filtered_attributes = filter_pycg(module, call_graph)
        logger.info(f"Attributes to keep based on PyCG: {filtered_attributes}")

        # Step 6.2 - Debloat the module
        debloat(appname, module, filtered_attributes)

        # TODO: Add stats collection
        # Re-import to update alive_modules
        new_report = run_profiler(modules_to_debloat)
        update_alive_modules(alive_modules, new_report)

    # --------------------------------------------------------------------- #
    # ---------------------- Stats-collecting Phase ----------------------- #
    # --------------------------------------------------------------------- #

    # Step 7 - Collect statistics

    # Run profiler again to collect statistics
    final_report = run_profiler(imported_modules)
    logger.info("Final report after debloating:")
    logger.info(pp(final_report))

    # --------------------------------------------------------------------- #
    # ------------------------------- Done -------------------------------- #
    # --------------------------------------------------------------------- #

    print("Debloating process completed successfully!")
    print("For detailed statistics, check the logs.")
