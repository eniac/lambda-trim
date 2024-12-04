# if python versionh is 3.11 or higher, use the sys.stdlib_module_names
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
