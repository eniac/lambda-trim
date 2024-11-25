import argparse
from ltrim.moduify.moduifier import Moduify
from ltrim.moduify.utils import magic_attributes

__all__ = ["Moduify", "magic_attributes"]


def main():
    parser = argparse.ArgumentParser(
        description="Modify modules by removing attributes."
    )
    parser.add_argument(
        "module_name", type=str, help="Name of the module to modify."
    )
    parser.add_argument(
        "-r",
        "--remove",
        action="store_true",
        help="Remove or keep attributes. If set, attributes are removed. Otherwise, they are kept.",
    )
    parser.add_argument(
        "-a",
        "--attributes",
        type=str,
        nargs="+",
        help="Attributes to remove or keep.",
    )

    args = parser.parse_args()

    moduifier = Moduify(module_name=args.module_name)
    moduifier.modify(args.attributes, remove=args.remove)
