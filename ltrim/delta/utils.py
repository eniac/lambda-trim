import os
import subprocess

driver_path = os.path.dirname(__file__) + "/driver.py"


class Found(Exception):
    pass


class PyLambdaRunner:
    """
    Class to run a Python file with a handler function and test cases.

    :param file_path: The path to the Python file to run
    :param handler: The handler function to run
    :param test_cases: The test cases to run
    """

    def __init__(self, file_path, handler="handler", test_cases="data.json"):
        self.file_path = file_path
        self.handler = handler
        self.test_cases = test_cases

    def run(self):
        try:
            process = subprocess.run(
                [
                    "python",
                    driver_path,
                    self.file_path,
                    "--handler",
                    self.handler,
                    "--test",
                    self.test_cases,
                ],
                capture_output=True,
                check=True,
            )

            return process
        except subprocess.CalledProcessError as e:
            return e


def chunks(xs, n):
    """
    Yield n chunks from xs.

    :param xs: The list to chunk
    :param n: The number of the chunks
    """
    k, m = divmod(len(xs), n)
    return (
        # fmt: off
        xs[i * k + min(i, m) : (i + 1) * k + min(i + 1, m)]
        for i in range(n)
        # fmt: on
    )


def flatten(lst):
    """
    Flatten a list of lists

    :param lst: The list to flatten
    """
    return [item for sublist in lst for item in sublist]
