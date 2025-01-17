import csv
from typing import NewType

DeltaRecord = NewType("DeltaRecord", tuple[float, int, int])


class Stats:
    """
    Class to store statistics about the debloating process

    :param appname: The name of the application
    :param top_K: The number of modules to debloat
    """

    def __init__(self, appname, top_K):
        self.stats = {}
        self.appname = appname.strip(".py")
        self.top_K = top_K

    def add_module(self, module):
        """
        Add a module to the internal dictionary

        :param module: The module to add
        """
        self.stats[module] = ModuleRecord(module)

    def set_profiling_stats(self, module, memory, time, before=True):
        """
        Set stats after profiling

        :param module: The module to set the stats for
        :param memory: Memory (in MB)
        :param time: Time (in ms)
        :param before: Whether the profiling happened before or after DD
        """
        order = "Pre" if before else "Post"
        self.stats[module].set_profiling_stats(memory, time, order)

    def set_debloating_stats(self, module, debloat_record: DeltaRecord):
        """
        Set the debloating stats

        :param module: The module to set the stats for
        :param debloat_record: The debloating stats
        """
        self.stats[module].set_debloating_stats(debloat_record)

    def set_path(self, module, path):
        """
        Set the path to the module file

        :param module: The module to set the stats for
        :param path: The path to the module file
        """
        self.stats[module].set_path(path)

    def convert_to_csv(self):
        """
        Convert the internal dictionary to a CSV
        """

        filename = f"log/{self.appname}_{self.top_K}_stats.csv"
        keys = [
            "Module",
            "Pre Memory",
            "Pre Import Time",
            "Post Memory",
            "Post Import Time",
            "Debloat Time",
            "Pre Attributes",
            "Removed Attributes",
            "Path",
        ]

        with open(filename, mode="w", encoding="utf-8") as file:

            writer = csv.DictWriter(file, fieldnames=keys)
            writer.writeheader()

            for _, record in self.stats.items():
                row = record.convert_to_row()
                writer.writerow(row)


class ModuleRecord:
    """
    Class to store statistics about the debloating process
    of a module

    :param module_name: The module to be debloated
    :param path: The path to the module file
    """

    def __init__(self, module_name):
        self.module_name = module_name
        self.stats = {}
        self.path = None

    def set_profiling_stats(self, memory, time, order):
        """
        Set stats after profiling

        :param memory: Memory (in MB)
        :param time: Time (in ms)
        :param before: Whether the profiling happened before or after DD
        """
        self.stats[order + " Memory"] = memory
        self.stats[order + " Import Time"] = time

    def set_debloating_stats(self, debloat_record: DeltaRecord):
        """
        Set the debloating stats

        :param debloat_time: Time taken to debloat the module (in ms)
        :param attributes_before: Number of module's attributes before debloating
        :param attributes_after: Number of module's attributes after debloating
        """
        debloat_time, attributes_before, attributes_after = debloat_record

        self.stats["Debloat Time"] = debloat_time
        self.stats["Pre Attributes"] = attributes_before
        self.stats["Removed Attributes"] = attributes_after

    def set_path(self, path):
        """
        Set the path to the module file

        :param path: The path to the module file
        """
        self.path = path

    def convert_to_row(self):
        """
        Convert the internal dictionary to a CSV row
        """

        row = {
            "Module": self.module_name,
            "Pre Memory": self.stats["Pre Memory"],
            "Pre Import Time": self.stats["Pre Import Time"],
            "Post Memory": self.stats["Post Memory"],
            "Post Import Time": self.stats["Post Import Time"],
            "Debloat Time": self.stats["Debloat Time"],
            "Pre Attributes": self.stats["Pre Attributes"],
            "Removed Attributes": self.stats["Removed Attributes"],
            "Path": self.path,
        }

        return row
