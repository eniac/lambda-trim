import argparse
import logging

from ltrim.debloat.debloat import Debloater
from ltrim.utils import mkdirp

# Create the log directory if it doesn't exist
mkdirp("log")

logger = logging.getLogger(__name__)
logging.basicConfig(
    filename="log/debloat.log",
    filemode="w",
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)


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
        "-s",
        "--scoring",
        default="cost",
        choices=["cost", "time", "memory", "random"],
        help="The scoring method to calculate the top K ranking of the modules.",
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

    debloater = Debloater(
        filename=args.filename,
        top_K=args.top_K,
        scoring=args.scoring,
        disable_pycg=args.no_pycg,
    )

    debloater.debloat()

    # --------------------------------------------------------------------- #
    # ------------------------------- Done -------------------------------- #
    # --------------------------------------------------------------------- #

    print("Debloating process completed successfully!")
    print("For detailed statistics, check the logs.")
