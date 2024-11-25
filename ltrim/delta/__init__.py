import argparse
from ltrim.delta.delta import DeltaDebugger
from ltrim.delta.utils import run_target

__all__ = [
    "DeltaDebugger",
    "run_target",
]


def main():

    parser = argparse.ArgumentParser(
        description="Run Delta Debugging on a module with a target program and a set of attributes to keep."
    )
    parser.add_argument("target", help="The target program")
    parser.add_argument("module", help="The module to modify")
    parser.add_argument(
        "attributes", type=str, nargs="+", help="Attributes to keep."
    )

    args = parser.parse_args()

    debugger = DeltaDebugger(
        target=args.target,
        module_name=args.module,
        marked_attributes=args.attributes,
    )

    remaining_attributes = debugger.delta_debug()
    print(f"Remaining attributes: {remaining_attributes}")
