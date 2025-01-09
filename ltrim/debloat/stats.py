class ModuleRecord:
    """
    Class to store statistics about the debloating process
    of a module

    :param module_name: The module to be debloated
    :param path: The path to the module file
    """

    def __init__(self, module_name, path):
        self.module_name = module_name
        self.stats = {}
        self.path = path

    def set_profiling_stats(self, memory, time, before=True):
        """
        Set stats after profiling

        :param memory: Memory (in MB)
        :param time: Time (in ms)
        :param before: Whether the profiling happened before or after DD
        """
        order = "before" if before else "after"
        self.stats["memory_" + order] = memory
        self.stats["time_" + order] = time

    def set_debloating_stats(self, debloat_time, attributes_before, attributes_after):
        """
        Set the debloating stats

        :param debloat_time: Time taken to debloat the module (in ms)
        :param attributes_before: Number of module's attributes before debloating
        :param attributes_after: Number of module's attributes after debloating
        """
        self.stats["debloat_time"] = debloat_time
        self.stats["attributes_before"] = attributes_before
        self.stats["attributes_after"] = attributes_after

    def convert_to_row(self):
        """
        Convert the internal dictionary to a CSV row
        """

        row = {
            "Module": self.module_name,
            "Pre Memory": self.stats["memory_before"],
            "Pre Import Time": self.stats["time_before"],
            "Post Memory": self.stats["memory_after"],
            "Post Import Time": self.stats["time_after"],
            "Debloat Time": self.stats["debloat_time"],
            "Pre Attributes": self.stats["attributes_before"],
            "Removed Attributes": self.stats["attributes_after"],
            "Path": self.path,
        }

        return row
