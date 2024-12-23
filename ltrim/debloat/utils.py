# if python versionh is 3.11 or higher, use the sys.stdlib_module_names
import random
import re
import sys
from functools import wraps
from multiprocessing import Pipe, Process

if sys.version_info >= (3, 11):
    blacklist = sys.stdlib_module_names
else:
    blacklist = [
        "ast",
        "argparse",
        "os",
        "sys",
        "shutil",
        "stat",
        "importlib",
        "re",
        "json",
        "time",
    ]


def isolate(func):
    """
    A decorator to run a function in a separate process and send its return value
    through a pipe.
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        # Create a pipe for communication
        parent_conn, child_conn = Pipe()

        def target(pipe_conn, *args, **kwargs):
            # Call the wrapped function and send the result through the pipe
            result = func(*args, **kwargs)
            pipe_conn.send(result)
            pipe_conn.close()  # Close the pipe connection after sending the result

        # Run the function in a separate process, passing the child pipe connection
        process = Process(target=target, args=(child_conn, *args), kwargs=kwargs)
        process.start()
        process.join()  # Wait for the process to complete

        # Return the parent pipe connection for the caller to retrieve the result
        return parent_conn.recv()

    return wrapper


def scoring(method, t, m, T, M):
    """
    The scoring method to calculate the top K ranking of the modules.

    :param method: The scoring method to use
    :param t: The import time of the module
    :param m: The memory usage of the module
    :param T: The total import time of the application
    :param M: The total memory usage of the application
    :return: The score of the module based on the scoring method
    """
    if method == "time":
        return t
    elif method == "memory":
        return m
    elif method == "cost":
        return (T - t) * m + t * M
    elif method == "random":
        return random.random()
    else:
        raise ValueError(
            "Invalid scoring method. Choose from 'time', 'memory', 'cost' or 'random'."
        )


def sort_report(report, method, T, M):
    """
    Sort the profiling report based on the scoring method.

    :param report: The profiling report to sort
    :param method: The scoring method to use for sorting
    :return: The sorted list of modules based on the scoring method
    """

    # Add scoring to the report
    for entry in report:
        print(entry)
        report[entry]["score"] = scoring(
            method,
            report[entry]["time"],
            report[entry]["memory"],
            T,
            M,
        )

    # Step 4: Sort the modules based on the scoring method
    return sorted(report.items(), key=lambda x: x[1]["score"], reverse=True)


def filter_pycg(module, pycg_attributes):
    """
    Filter the PyCG attributes by keeping only the ones that are in the module.

    :param module: The module to filter the attributes
    :param pycg_attributes: The PyCG attributes to filter
    :return: The filtered PyCG attributes
    """

    # using regex to match the module name, i.e. "module.*"
    pattern = re.compile(r"{}.*".format(module))
    return [attr for attr in pycg_attributes if pattern.match(attr)]
