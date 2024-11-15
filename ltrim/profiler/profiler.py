import os
import sys
import time
import psutil
from importlib.machinery import PathFinder
from importlib.abc import Loader
from contextlib import contextmanager
from types import ModuleType, MethodType
from typing import Sequence

from ltrim.utils.constants import MB, MS


@contextmanager
def profiler_context(profiler, operation_name, counter):
    """
    Context manager for profiling memory and execution time.
    """
    process = psutil.Process(os.getpid())
    start_time = time.time()
    memory_before = process.memory_info().rss

    yield  # This allows the context to be used around any code block

    memory_after = process.memory_info().rss
    end_time = time.time()

    memory_footprint = memory_after - memory_before
    time_taken = end_time - start_time

    profiler[operation_name] = {
        "order": counter,
        "memory": memory_footprint / MB,
        "time": time_taken / MS,
    }


def create_profiler_loader(
    loader: Loader, profiler: dict[str, dict[str, float]], counter: int
):
    """
    Create a loader with profiler attached, based on the original loader
    """

    loader_exec_module = loader.exec_module

    def profiler_exec_module(self, module: ModuleType):
        """
        Execute the module and profile the memory, time footprint
        """
        module_name = module.__name__

        # only record one time
        if module_name not in profiler:
            with profiler_context(profiler, module_name, counter):
                loader_exec_module(module)
        else:
            loader_exec_module(module)

    loader.exec_module = MethodType(profiler_exec_module, loader)

    return loader


class ProfilerMetaFinder(PathFinder):
    """
    Custom meta path finder to time the import of modules
    """

    profiler_report: dict[str, dict[str, float]] = {}
    counter = 0

    @classmethod
    def find_spec(
        cls,
        fullname: str,
        path: Sequence[str] | None = None,
        target: ModuleType | None = None,
    ):
        """
        Find the spec for the given module, delegate to the
        original implementation and replace with our own loader
        """

        spec = super().find_spec(fullname, path, target)
        if spec and spec.loader:
            cls.counter += 1
            spec.loader = create_profiler_loader(
                spec.loader, cls.profiler_report, cls.counter
            )
        return spec


def attach():
    sys.meta_path.insert(0, ProfilerMetaFinder())


def detach():
    sys.meta_path = [i for i in sys.meta_path if not isinstance(i, ProfilerMetaFinder)]


def get_profiler_report():
    """
    Return the profiler report
    """
    return ProfilerMetaFinder.profiler_report
