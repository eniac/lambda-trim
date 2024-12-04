# if python versionh is 3.11 or higher, use the sys.stdlib_module_names
import sys

if sys.version_info >= (3, 11):
    blacklist = sys.stdlib_module_names
else:
    blacklist = [
        "ast",
        "argparse",
        "os",
        "sys",
        "shutil",
        "stat",
        "importlib",
        "re",
        "json",
        "time",
    ]


def clear_module_cache(module_names):
    """
    Clear the module cache for the given module names.

    :param module_names: List of module names
    """
    for module_name in module_names:
        if module_name in sys.modules:
            print(f"Removing {module_name} from sys.modules")
            del sys.modules[module_name]
