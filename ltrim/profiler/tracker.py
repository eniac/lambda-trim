"""track all imported modules for a Python file"""

import sys
from importlib.abc import Loader
from importlib.machinery import PathFinder
from types import MethodType, ModuleType
from typing import Sequence


def create_tracker_loader(loader: Loader, record: set[str]):
    """
    Create a loader with profiler attached, based on the original loader
    """

    loader_exec_module = loader.exec_module

    def tracker_exec_module(self, module: ModuleType):
        """
        Execute the module and profile the memory, time footprint
        """
        module_name = module.__name__

        # only record one time
        if module_name not in record:
            record.add(module_name)

        loader_exec_module(module)

    loader.exec_module = MethodType(tracker_exec_module, loader)

    return loader


class TrackerMetaFinder(PathFinder):
    """
    Custom meta path finder to time the import of modules
    """

    record: set[str] = set()

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
            spec.loader = create_tracker_loader(spec.loader, cls.record)
        return spec


def attach():
    sys.meta_path.insert(0, TrackerMetaFinder())


def detach():
    sys.meta_path = [i for i in sys.meta_path if not isinstance(i, TrackerMetaFinder)]


def get_tracker_report():
    """return the profiler report"""
    return TrackerMetaFinder.record
