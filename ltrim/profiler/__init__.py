import os

import psutil

import ltrim.profiler.profiler as profiler
import ltrim.profiler.tracker as tracker
from ltrim.utils import MB


def get_memory_usage():
    """
    Get the memory usage of the current process in MB.
    """
    process = psutil.Process(os.getpid())
    return process.memory_info().rss / MB


__all__ = ["profiler", "tracker"]
