import subprocess


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


def chunks(xs, n):
    """
    Yield successive n-sized chunks from lst.
    https://stackoverflow.com/a/312464

    :param xs: The list to chunk
    :param n: The size of the chunks
    """
    n = max(1, n)
    return (xs[i : i + n] for i in range(0, len(xs), n))


def flatten(lst):
    """
    Flatten a list of lists

    :param lst: The list to flatten
    """
    return [item for sublist in lst for item in sublist]
