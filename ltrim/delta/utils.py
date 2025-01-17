import os
import subprocess

driver_path = os.path.abspath(__file__).replace("utils.py", "driver.py")


class Found(Exception):
    pass


class PyLambdaRunner:
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
