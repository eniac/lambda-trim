import os
import shutil


def cp(source_path, destination_path):
    """
    Copy a file from source to destination.
    Same functionality as: cp src dst

    :param source_path: Source file path
    :param destination_path: Destination file path
    """

    # Create the destination directory if it doesn't exist
    destination_dir = os.path.dirname(destination_path)
    if not os.path.exists(destination_dir):
        os.makedirs(destination_dir)

    # If the destination file exists, remove it
    if os.path.exists(destination_path):
        os.remove(destination_path)

    # Copy the file to the destination
    shutil.copy2(source_path, destination_path)


def mkdirp(directory_path):
    """
    Same functionality as: mkdir -p dir
    """

    if os.path.exists(directory_path):
        shutil.rmtree(directory_path)
    os.makedirs(directory_path)
