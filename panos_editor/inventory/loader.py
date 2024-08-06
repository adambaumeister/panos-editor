import pathlib

from panos_editor.inventory.file import FileInventory


def get_inventory(
        file_inventory_directory=pathlib.Path(".")
):
    """
    Manages returning the inventory based on given configuration, environment, and default settings.
    """
    return FileInventory(
        directory=file_inventory_directory
    )