import importlib
import time

from pycg import formats
from pycg.pycg import CallGraphGenerator
from pycg.utils.constants import CALL_GRAPH_OP

from ltrim.debloat.utils import isolate
from ltrim.delta import DeltaDebugger
from ltrim.profiler import get_memory_usage, profiler


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
def run_profiler(modules):
    """
    Profile the import process of a list of modules.

    :param modules: A list of modules to profile
    """
    profiler.attach()

    starting_memory = get_memory_usage()

    for module in modules:
        importlib.import_module(module)

    ending_memory = get_memory_usage()

    profiler_report = profiler.get_report()
    profiler_report["total_memory"] = ending_memory - starting_memory

    profiler.detach()

    return profiler_report


@isolate
def debloat(target, module, marked_attributes):
    """
    Run the DeltaDebugger to debloat a module imported from the target program.

    :param target: The target program to run
    :param module: The module to debloat
    :param marked_attributes: The marked attributes to keep
    """

    delta_debugger = DeltaDebugger(target, module, marked_attributes)

    start = time.time()
    debloated_attributes = delta_debugger.delta_debug(log=True)
    end = time.time()
    total_time = end - start

    print(f"Total time taken: {total_time}")
    print(debloated_attributes)

    delta_debugger.finalize_module(debloated_attributes)

    return
