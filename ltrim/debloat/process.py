from functools import wraps
from multiprocessing import Pipe, Process

from pycg import formats
from pycg.pycg import CallGraphGenerator
from pycg.utils.constants import CALL_GRAPH_OP

from ltrim.profiler import profiler


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


@isolate
def run_pycg(target):
    """
    Run PyCG to exctract the call graph of the target program.

    :param target: The target program to run
    :param output_dict: The output dictionary to store the call graph
    """
    cg = CallGraphGenerator([target], None, -1, CALL_GRAPH_OP)
    cg.analyze()

    simple_formatter = formats.Simple(cg)
    return list(simple_formatter.generate().keys())


@isolate
def profile(modules):
    """
    Profile the import process of a list of modules.

    :param modules: A list of modules to profile
    """

    profiler.attach()

    profiler.detach()
