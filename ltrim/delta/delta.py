import ast
import sys
import importlib
from ltrim.moduify import Moduify
from ltrim.utils import mkdirp, MAGIC_ATTRIBUTES
from ltrim.delta.utils import run_target, chunks, flatten


class DeltaDebugger:
    """
    Delta Debugger instance
    """

    def __init__(self, target, module_name, marked_attributes):

        # Target program to run
        self.target = target

        # Attributes that must be kept
        self.marked_attrs = marked_attributes

        # Initialize the Moduify instance
        self.module_name = module_name
        self.moduifier = Moduify(
            module_name=self.module_name,
            marked_attrs=self.marked_attrs,
        )

        self.stats = {"iterations": 0, "attrs": (0, 0)}

        # Create a logging directory for intermediate results
        mkdirp("log/" + self.module_name + "/iterations")

        process = run_target(self.target)

        if process.returncode == 0:
            self.original_output = str(process.stdout, "utf-8")
            # logger.info("Original output: %s", self.original_output)
        else:
            print(f"Error running target program {process.stderr}")
            # sys.exit(1)
        sys.exit(1)

    def oracle(self, attributes):
        """
        Run the target program with the modified module and attributes.
        If the program fails to run, the oracle returns False.
        Otherwise, it compares the output of the program with the
        original output.

        :param attributes: The attributes under test
        """

        self.stats["iterations"] += 1
        iterations = self.stats["iterations"]

        try:

            modified_ast = self.moduifier.modify(attributes, remove=False)

            iteration_dir = (
                "log/" + self.module_name + "/iterations/i" + str(iterations)
            )
            mkdirp(iteration_dir)

            with open(
                iteration_dir + "/__init__.py", "w", encoding="utf-8"
            ) as file:
                new_source = ast.unparse(modified_ast)
                file.write(new_source)

            with open(
                iteration_dir + "/attr.txt", "w", encoding="utf-8"
            ) as file:
                file.write("Keeping the following attributes:\n")
                for item in attributes:
                    file.write(f"{item}\n")

        except Exception as e:

            # logger.error("Error modifying module: %s", e)
            print(f"Error modifying module: {e}")

            return False

        process = run_target(self.target)

        if process.returncode == 0:
            # logger.info("Output: %s", str(process.stdout, "utf-8"))
            output = str(process.stdout, "utf-8")

            if output != self.original_output:
                pass
                # logger.info("Output changed: %s", output)
                # logger.info("Original output: %s", self.original_output)

            return output == self.original_output

        return False

    def delta_debug(self):
        """
        Delta-Debugging algorithm
        """

        if self.moduifier.ast is None:
            print("Module is not a Python file")
            return []

        print("Running Delta Debugging for module " + self.module_name)

        # logger.info("Running Delta Debugging for module %s", self.module_name)
        # logger.info("Necessary attributes: %s", self.marked_attrs)

        module = importlib.import_module(self.module_name)

        members = [x for x in dir(module) if x not in MAGIC_ATTRIBUTES]
        # logger.info("Module attributes: %s", members)

        remaining_attrs, n = members, 2

        size_module = len(dir(module))
        attrs_before = len(remaining_attrs)

        while n <= len(remaining_attrs):

            us = chunks(remaining_attrs, n)

            flag = False

            for i in range(n):

                attributes = us[i]
                # logger.info("Trying partition %s", attributes)

                if self.oracle(attributes):

                    remaining_attrs, n = attributes, 2
                    # logger.info("REDUCED to %s", l)
                    flag = True

                    break

            if flag:

                continue

            if n > 2:

                flag = False

                for i in range(n):

                    _coattributes = us.copy()
                    _coattributes.pop(i)
                    coattributes = flatten(_coattributes)
                    # logger.info("Trying complements %s", coattributes)

                    if self.oracle(coattributes):

                        remaining_attrs, n = coattributes, n - 1
                        # logger.info("REDUCED to %s", l)
                        flag = True

                        break

            if flag:

                continue

            n *= 2

        attrs_after = len(remaining_attrs)
        removed = attrs_before - attrs_after
        print(
            f"Removed {removed} attributes {(removed / size_module * 100):.2f}%."
        )
        self.stats["attrs"] = (size_module, removed)
        return list(self.marked_attrs) + remaining_attrs

    def get_attr_stats(self):
        """
        Wrapper around stats collection
        """
        return self.stats["attrs"], self.stats["iterations"]

    def finalize_module(self, attributes, local=False):
        """
        Finalize the module by removing the attributes
        left after delta debugging

        :param attributes: The attributes to remove
        :param local: If working on a local environment, restore the original directory
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

        with open(
            log_mod_dir + "/original_" + basename, "w", encoding="utf-8"
        ) as file:
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
