from typing import Callable
from panos_editor.parser.xml import PanosObjectCollection, PanosObject


class SelectQuery:
    def __init__(self, path: list[str]):
        """
        A select query. Used to split PanosObjects into smaller collections.

        Examples:
            >>> q = SelectQuery(["shared", "address"])
        """
        self.path = path

    def __call__(self, collection: PanosObjectCollection):
        return PanosObjectCollection(self.select_object_recurse(list(collection), self.path))

    def select_object_recurse(self, objects: list[PanosObject], path: list[str]):
        result = []

        for object in objects:
            if len(path) == 0:
                # If this is the endpoint of the object, see if it has <entry> members

                entry_children = object.children.get("entry")
                if entry_children:
                    result += entry_children
                else:
                    # Otherwise, just add this single object
                    result.append(object)
            else:
                child_objects = object.children.get(path[0])
                if child_objects:
                    result += self.select_object_recurse(child_objects, path[1:])

        return result


class SearchQuery:
    def __init__(
            self, relative_path: list[str], search_function: Callable
    ):
        """
        A single search query.

        Examples:
            >>> from panos_editor.parser.query_functions import ExactOrIn
            >>> q = SearchQuery(["tag"], ExactOrIn("DEMO-STATIC"))
        """
        self.relative_path = relative_path
        self.search_function = search_function

    def __call__(self, collection: PanosObjectCollection):
        return self.search_objects(list(collection), self.relative_path)

    def search_objects(self, objects: list[PanosObject], path: list[str]):
        """
        Search the list of objects (the collection) for the element specified and returns all matching.

        This returns the top level objects only.
        """
        result = []
        for obj in objects:
            if self.search_objects_recursive([obj], path):
                result.append(obj)

        return result

    def search_objects_recursive(self, objects: list[PanosObject], path: list[str]):
        match = False

        key = ""
        if len(path) > 0:
            key = path[0]

        for obj in objects:
            # Handle the case where the search path doesn't include the final identifier
            member_value = obj.elements.get("member")
            if len(path) == 0 and member_value:
                if self.search_function(member_value):
                    match = True

            element_value = obj.elements.get(key)
            if len(path) == 1 and element_value:
                if self.search_function(element_value):
                    match = True

            # Treat 'entry' as a special child so the user doesn't have to explicitly ask for it
            next_obj = obj.children.get(key)
            if next_obj:
                next_path = path[1:]
                match = self.search_objects_recursive(next_obj, next_path)

            next_obj = obj.children.get("entry")
            if next_obj:
                match = self.search_objects_recursive(next_obj, path)

        return match