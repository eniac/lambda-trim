import ast
import importlib
import logging
import sys
import time

from ltrim.delta.utils import Found, PyLambdaRunner, chunks, flatten
from ltrim.moduify import Moduify
from ltrim.utils import MAGIC_ATTRIBUTES, DeltaRecord, mkdirp


class DeltaDebugger:
    """
    Delta Debugger instance

    :param target: The target program to run
    :param module_name: Name of the module to debloat
    :param marked_attributes: Attributes that must be kept
    """

    def __init__(self, target, module_name, marked_attributes, test_cases="data.json"):
        # Attributes that must be kept
        self.marked_attrs = marked_attributes

        # Initialize the Moduify instance
        self.module_name = module_name
        self.moduifier = Moduify(
            module_name=self.module_name,
            marked_attributes=self.marked_attrs,
        )

        # Initialize the logger for the module under DD
        self.logger = logging.getLogger(module_name + "_delta")
        self.logger.setLevel(logging.INFO)
        handler = logging.FileHandler(f"log/{module_name}_delta.log")
        handler.setLevel(logging.INFO)
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self.logger.propagate = False

        self.iterations = 0

        # Create a logging directory for intermediate results
        mkdirp("log/" + self.module_name + "/iterations")

        # Instace of driver for running the target program
        self.runner = PyLambdaRunner(file_path=target, test_cases=test_cases)

        process = self.runner.run()

        if process.returncode == 0:
            self.original_output = str(process.stdout, "utf-8")
            self.logger.info("Original output: %s", self.original_output)
        else:
            self.logger.error(f"Error running target program: {process.stderr}")
            sys.exit(1)

    def oracle(self, attributes, log=True):
        """
        Run the target program with the modified module and attributes.
        If the program fails to run, the oracle returns False.
        Otherwise, it compares the output of the program with the
        original output.

        :param attributes: The attributes under test
        """

        self.iterations += 1

        if log:
            try:
                modified_ast = self.moduifier.modify(attributes, remove=False)

                iteration_dir = (
                    "log/" + self.module_name + "/iterations/i" + str(self.iterations)
                )
                mkdirp(iteration_dir)

                with open(
                    iteration_dir + "/__init__.py", "w", encoding="utf-8"
                ) as file:
                    new_source = ast.unparse(modified_ast)
                    file.write(new_source)

                with open(iteration_dir + "/attr.txt", "w", encoding="utf-8") as file:
                    file.write("Keeping the following attributes:\n")
                    for item in attributes:
                        file.write(f"{item}\n")

            except Exception as e:
                self.logger.error("Error modifying module: %s", e)
                print(f"Error modifying module: {e}")

                return False

        process = self.runner.run()

        if process.returncode == 0:
            self.logger.info("Output: %s", str(process.stdout, "utf-8"))
            output = str(process.stdout, "utf-8")

            if output != self.original_output:
                self.logger.info("Output changed: %s", output)
                self.logger.info("Original output: %s", self.original_output)
                return False

            return output == self.original_output

        else:
            self.logger.error("Error running target program: %s", process.stderr)
            return False

    def delta_debug(self, log=False):
        """
        Delta-Debugging algorithm
        """

        start = time.time()

        if self.moduifier.ast is None:
            print("Module is not a Python file")
            return []

        print("Running Delta Debugging for module " + self.module_name)

        self.logger.info("Running DeltaDebugging for module %s", self.module_name)
        self.logger.info("Necessary attributes: %s", self.marked_attrs)

        module = importlib.import_module(self.module_name)

        members = [x for x in dir(module) if x not in MAGIC_ATTRIBUTES]
        self.logger.info("Module attributes: %s", members)

        remaining_attrs, n = members, 2

        all_attributes = len(dir(module))
        attrs_before = len(remaining_attrs)

        while n <= len(remaining_attrs):
            us = list(chunks(remaining_attrs, n))

            try:
                for i in range(n):
                    attributes = us[i]

                    self.logger.info("Trying partition %s", attributes)

                    if self.oracle(attributes, log):
                        remaining_attrs, n = attributes, 2
                        raise Found

                if n > 2:
                    for i in range(n):
                        coattributes = us.copy()
                        coattributes.pop(i)
                        coattributes = flatten(coattributes)

                        self.logger.info("Trying c-partition %s", coattributes)

                        if self.oracle(coattributes, log):
                            remaining_attrs, n = coattributes, n - 1
                            raise Found

                n *= 2

            except Found:
                self.logger.info("REDUCED to %s", remaining_attrs)
                continue

        end = time.time()
        debloat_time = end - start
        print(f"Total time taken to debloat {self.module_name}: {debloat_time:.2f}ms")

        self.logger.info("Remanining attributes: %s", remaining_attrs)

        attrs_after = len(remaining_attrs)
        removed = attrs_before - attrs_after
        print(f"Removed {removed} attributes {(removed / all_attributes * 100):.2f}%.")

        delta_record = DeltaRecord((debloat_time, all_attributes, attrs_after))

        return list(self.marked_attrs) + remaining_attrs, delta_record

    def get_attr_stats(self):
        """
        Wrapper around iterations stats
        """
        return self.iterations

    def finalize_module(self, attributes, local=False):
        """
        Finalize the module by removing a set of attributes

        :param attributes: The attributes to remove
        :param local: In local environment, restore the original directory
        """

        m_path = self.moduifier.module_path

        if self.moduifier.ast is None:
            return m_path

        m_ast = self.moduifier.modify(attributes, remove=False)

        basename = self.moduifier.basename
        log_mod_dir = "log/" + self.module_name

        # Log the modified attributes
        attributes_log = log_mod_dir + "/attrs.txt"
        with open(attributes_log, "w", encoding="utf-8") as file:
            for item in attributes:
                file.write(f"{item}\n")
            file.flush()

        # Log the modified and the original __init__.py files
        mod_init_path = log_mod_dir + "/" + basename
        with open(mod_init_path, "w", encoding="utf-8") as file:
            new_source = ast.unparse(m_ast)
            file.write(new_source)
            file.flush()

        with open(log_mod_dir + "/original_" + basename, "w", encoding="utf-8") as file:
            with open(
                self.moduifier.backup_dir + "/" + basename,
                "r",
                encoding="utf-8",
            ) as f:
                file.write(f.read())
                file.flush()

        if local:
            self.moduifier.restore_original_directory()

        return m_path
