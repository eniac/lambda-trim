import argparse

from ltrim.debloat.debloat import Debloater
from ltrim.utils import Config


def main():
    parser = argparse.ArgumentParser(
        prog="debloat",
        description="""Debloat a Python application by removing unused
        attributes of imported modules.""",
        epilog="""Developed and maintained by Spyros Pavlatos. Originally created
        in the Distributed Systems Laboratory at University of Pennsylvania""",
    )

    parser.add_argument("filename", type=str, help="Name of the application")

    parser.add_argument(
        "-k", "--top-K", type=int, default=10, help="Number of modules to debloat."
    )

    parser.add_argument(
        "-t",
        "--testcases",
        type=str,
        default="data.json",
        help="Path to the testcases file.",
    )

    parser.add_argument(
        "-s",
        "--scoring",
        default="cost",
        choices=["cost", "time", "memory", "random", "custom"],
        help="The scoring method to calculate the top K ranking of the modules.",
    )

    parser.add_argument(
        "-H",
        "--handler",
        default="handler",
        help="""The name of the function handler.
        This should be the entry point of the application""",
    )

    # Disable PyCG flag
    parser.add_argument(
        "--no-pycg",
        action="store_true",
        help="""Do not use PyCG for the debloating
        process. This will result in a slower debloating
        process.""",
    )

    args = parser.parse_args()

    # create a configuration
    config = Config(
        appname=args.filename,
        handler=args.handler,
        test_cases=args.testcases,
    )

    debloater = Debloater(
        config=config,
        top_K=args.top_K,
        scoring=args.scoring,
        disable_pycg=args.no_pycg,
    )

    debloater.run()
