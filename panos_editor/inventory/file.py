import pathlib
from lxml.etree import fromstring

from panos_editor.inventory.base import Loader
from panos_editor.inventory.errors import HostNotFound
from panos_editor.parser.xml import PanosObjectCollection, PanosObject


class FileLoader(Loader):
    def __init__(self, file: pathlib.Path):
        """
        Basic File type Loader. Reads local configuration files and turns them into PanosObjectCollection() instances.

        Arguments:
            file: The path to the configuration file.
        """
        self.file = file

    def __call__(self) -> PanosObjectCollection:
        return PanosObjectCollection([PanosObject.from_xml(fromstring(open(self.file).read()))])


class FileInventory:
    def __init__(self, directory: pathlib.Path = pathlib.Path(".")):
        """
        FileInventory is a simple Inventory of configurations based in a single directory.

        Files in a `FileInventory` can be referenced by their literal name whenever you need to select them.
        """
        self.directory = directory

    def get_by_id(self, id: str):
        """
        Returns the relevant `FileLoader` instance based on the provided ID of the host in the inventory.

        In this case, ID always maps to the name of a file.
        """
        path = self.directory.joinpath(id)
        if not path.is_file():
            raise HostNotFound(
                f"{id} was not found in the given inventory directory ({self.directory})"
            )

        return FileLoader(path)
