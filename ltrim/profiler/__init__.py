import os

import psutil

import ltrim.profiler.profiler as profiler
from ltrim.utils import MB


def get_memory_usage():
    """
    Get the memory usage of the current process in MB.
    """
    process = psutil.Process(os.getpid())
    return process.memory_info().rss / MB


__all__ = ["profiler", "get_memory_usage"]
