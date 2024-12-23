import argparse
import ast

from ltrim.debloat.process import debloat, run_profiler, run_pycg
from ltrim.debloat.utils import blacklist, filter_pycg, sort_report
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
    imports_finder = ImportsFinder()
    imports_finder.visit(ast_source)

    # Step 2: Use PyCG to extract the call graph of the application
    call_graph = run_pycg(appname)
    print(call_graph)

    # --------------------------------------------------------------------- #
    # ------------------------ Constructing Phase ------------------------- #
    # --------------------------------------------------------------------- #

    # Step 3: Construct a list of the imported modules
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

    # Step 3: Profile the import process of the application
    report = run_profiler(imported_modules)

    import pprint as pp

    # Extract the total memory used by the imported modules
    total_memory = report["total_memory"]
    del report["total_memory"]

    # Extract the total time taken to import modules
    total_time = sum(
        [report[module]["time"] for module in imported_modules if module in report]
    )

    print(f"Total memory used: {total_memory}")
    print(f"Total time taken: {total_time}")

    # Step 5 - Sort the profiler report by the scoring method
    sorted_report = sort_report(report, args.scoring, total_time, total_memory)

    # Filter modules in the blacklist
    sorted_report = [module for module in sorted_report if module[0] not in blacklist]
    pp.pprint(sorted_report[: args.top_K])

    # TODO: Log statistics from the report

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
        print(filtered_attributes)

        # Step 6.2 - Debloat the module
        debloat(appname, module, filtered_attributes)

        # TODO: Add stats collection
        # Re-import to update alive_modules
        new_report = run_profiler(modules_to_debloat)

        for _module in alive_modules:
            if _module not in new_report:
                alive_modules.remove(_module)

    # --------------------------------------------------------------------- #
    # ---------------------- Stats-collecting Phase ----------------------- #
    # --------------------------------------------------------------------- #

    # Step 7 - Collect statistics

    # Run profiler again to collect statistics
    final_report = run_profiler(imported_modules)
    print(final_report)

    # --------------------------------------------------------------------- #
    # ------------------------------- Done -------------------------------- #
    # --------------------------------------------------------------------- #

    print("Debloating process completed successfully!")
    print("For detailed statistics, check the logs.")
