from typing import Callable

from panos_editor.parser.query_functions import ExactOrIn
from panos_editor.parser.xml import PanosObjectCollection, PanosObject


def get_value_recursive(obj: PanosObject, path: list[str]):
    """
    Recursively searches the object tree, returning value found at the given Path


    Examples:
        >>> get(get_value_recursive(PanosObject(...), ["source"]))
    """

    # Handle the case where the search path doesn't include the final identifier
    member_value = obj.elements.get("member")
    if len(path) == 0 and member_value:
        return member_value

    key = path[0]

    attr_value = obj.attrs.get(key)
    if attr_value:
        return attr_value

    element_value = obj.elements.get(key)
    if len(path) == 1 and element_value:
        return element_value

    # Treat 'entry' as a special child so the user doesn't have to explicitly ask for it
    children = obj.children.get(key)
    if children:
        next_path = path[1:]
        for child in children:
            return get_value_recursive(child, next_path)


class Join:
    def __init__(self, left_path: list[str], right_path: list[str]):
        """
        Implements the ability to 'join' multiple collections on user-specified common attributes between those collections.

        Examples:
            >>> j = Join(["name"], ["source"])
            >>> j(PanosObjectCollection(...), PanosObjectCollection(...))
        """
        self.left_path = left_path
        self.right_path = right_path

    def __call__(self, left: PanosObjectCollection, right: PanosObjectCollection, on_function: Callable = ExactOrIn):
        joined_objects = []
        for left_obj in left:
            left_value = get_value_recursive(left_obj, self.left_path)
            for right_obj in right:
                right_value = get_value_recursive(right_obj, self.right_path)
                if ExactOrIn(left_value)(right_value):
                    joined_objects.append(right_obj)

        return joined_objects


class And:
    def __init__(self, *predicates):
        """
        Implements 'AND' predicate logic

        Example
            >>> from panos_editor.parser.query_functions import ExactOrIn
            >>> q = And(SearchQuery(["tag"], ExactOrIn("DEMO-STATIC"), SearchQuery(["ip-netmask"], ExactOrIn("10.100.10.1"))
        """
        self.predicates = predicates

    def __call__(self, collection: PanosObjectCollection):
        result = collection
        for predicate in self.predicates:
            # Filter through the searchqueries such that only all matching results are returned
            result = predicate(result)

        return result


class SelectQuery:
    def __init__(self, path: list[str]):
        """
        A select query. Used to split PanosObjects into smaller collections.

        Examples:
            >>> q = SelectQuery(["shared", "address"])
        """
        self.path = path

    def __call__(self, collection: PanosObjectCollection):
        return PanosObjectCollection(
            self.select_object_recurse(list(collection), self.path)
        )

    def select_object_recurse(self, objects: list[PanosObject], path: list[str]):
        result = []
        for object in objects:
            entry_children = object.children.get("entry")
            if len(path) == 0:
                # If this is the endpoint of the object, see if it has <entry> members

                if entry_children:
                    result += entry_children
                else:
                    # Otherwise, just add this single object
                    result.append(object)
            elif entry_children:
                # don't trim the path in this scenario
                result += self.select_object_recurse(entry_children, path)
            else:
                child_objects = object.children.get(path[0])
                if child_objects:
                    result += self.select_object_recurse(child_objects, path[1:])

        return result


class SearchQuery:
    def __init__(self, relative_path: list[str], search_function: Callable):
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
