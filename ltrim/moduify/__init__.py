if __name__ == "__main__":
    modifier = Moduify(
        module_name="pandas.core.generic",
        build_path="build/",
        marked_attrs=[],
        magic_attrs=[],
    )
    modifier.modify(["weakref"], remove=True)
