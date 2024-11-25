import subprocess
from itertools import chain


def run_target(target: str, input: str = None):
    """
    Run the target program and return the process object

    :param target: The target program
    :param input: JSON file containing test cases for the program
    """

    try:
        if input is not None:
            pass
        else:
            process = subprocess.run(
                ["python", target, "2>>", "log/error.log"],
                capture_output=True,
                check=True,
            )
            return process

    except subprocess.CalledProcessError as e:
        print(e)
        return e


def chunks(lst, n):
    """
    Yield successive n-sized chunks from lst.
    https://stackoverflow.com/a/312464

    :param lst: The list to chunk
    :param n: The size of the chunks
    """
    for i in range(0, len(lst), n):
        yield lst[i : i + n]


def flatten(lst):
    """
    Flatten a list of lists

    :param lst: The list to flatten
    """
    return chain.from_iterable(lst)
