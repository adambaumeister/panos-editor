from typing import Callable, Union, Optional, Self

from panos_editor.inventory.file import FileLoader
from panos_editor.query.query_functions import ExactOrIn
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


class SimpleJoin:
    def __init__(
        self, left_path: list[str], right_path: list[str], join_func=ExactOrIn
    ):
        """
        Implements the ability to 'join' multiple collections on user-specified common attributes between those collections.

        This is an Inner Join implementation, returning only those objects that are teh asme between the two items.

        Examples:
            >>> j = InnerJoin(["name"], ["source"])
            >>> j(PanosObjectCollection(...), PanosObjectCollection(...))

        Note that this join function adds a reference to the joined objects to the original object.
        """
        self.left_path = left_path
        self.right_path = right_path
        self.join_func = join_func

    def __call__(
        self,
        left: PanosObjectCollection,
        right: PanosObjectCollection,
        on_function: Callable = ExactOrIn,
    ):
        joined_objects = []
        for left_obj in left:
            left_value = get_value_recursive(left_obj, self.left_path)
            for right_obj in right:
                right_value = get_value_recursive(right_obj, self.right_path)
                if self.join_func(left_value)(right_value):
                    left_obj.add_joined_object(right_obj)
                    right_obj.add_joined_object(left_obj)
                    joined_objects.append(right_obj)

        return joined_objects


class And:
    def __init__(self, *predicates):
        """
        Implements 'AND' predicate logic

        Example
            >>> from panos_editor.query.query_functions import ExactOrIn
            >>> q = And(SearchQuery(["tag"], ExactOrIn("DEMO-STATIC")), SearchQuery(["ip-netmask"], ExactOrIn("10.100.10.1")))
        """
        self.predicates = predicates

    def __call__(self, collection: PanosObjectCollection):
        result = collection
        for predicate in self.predicates:
            # Filter through the searchqueries such that only all matching results are returned
            result = predicate(result)

        return result


class Or:
    def __init__(self, *predicates):
        """
        Implements 'OR' predicate logic

        Example
            >>> from panos_editor.query.query_functions import ExactOrIn
            >>> q = Or(SearchQuery(["tag"], ExactOrIn("DEMO-STATIC")), SearchQuery(["ip-netmask"], ExactOrIn("10.100.10.1")))
        """
        self.predicates = predicates

    def __call__(self, collection: PanosObjectCollection):
        result_objects = []
        for predicate in self.predicates:
            result_objects += predicate(collection)

        return PanosObjectCollection(result_objects)


class SelectQuery:
    STATIC_DEVICE_GROUP_PATH = ["devices", "device-group"]
    STATIC_TEMPLATE_PATH = ["devices", "template"]
    STATIC_TEMPLATE_STACK_PATH = ["devices", "template-stack"]

    def __init__(self, path: list[str]):
        """
        A select query. Used to split PanosObjects into smaller collections.

        Select queries support names directly in the selection path as a shortcut. For example, `["OUTBOUND", "address"]` in place
        of `["device", "device-group:OUTBOUND", "address"],

        Examples:
            Select all Addresses from Shared

            >>> q = SelectQuery(["shared", "address"])

            Select all addresses from a named device-group - this also works for templates and template-stacks

            >>> q = SelectQuery(["OUTBOUND", "address"])
        """
        self.path = path

    def __call__(self, collection: PanosObjectCollection):
        result = self.select_object_recurse(list(collection), self.path)

        # Try using the device-group in the path
        if not result:
            result = self.select_object_recurse(
                list(collection), self.STATIC_DEVICE_GROUP_PATH + self.path
            )

        # Try using the template-stack in the path
        if not result:
            result = self.select_object_recurse(
                list(collection), self.STATIC_TEMPLATE_STACK_PATH + self.path
            )

        return PanosObjectCollection(result)

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
                named_objects = {x.attrs.get("name"): x for x in entry_children}
                if named_objects.get(path[0]):
                    # If we match a named object from an <entry> element
                    result += self.select_object_recurse(entry_children, path[1:])
                else:
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
            >>> from panos_editor.query.query_functions import ExactOrIn
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
            value = get_value_recursive(obj, path)
            if value:
                if self.search_function(value):
                    result.append(obj)

        return result


class Statement:
    def __init__(self, select: SelectQuery, search: Optional[Union[And, Or]] = None, loader: Optional[Union[FileLoader]] = None):
        """
        A complete statement for querying PAN-OS Objects.

        Arguments:
            select: The `SelectQuery` object for selecting the objects
            search: The top level predicate used in the search query
        """
        self.loader = loader
        self.select = select
        self.search = search

    def __call__(self, collection: Optional[PanosObjectCollection] = None):
        # If this statement defines a loader, use it instead of any passed collection
        if self.loader:
            collection = self.loader()

        selected = self.select(collection)
        if not self.search:
            return selected
        return self.search(selected)


class InnerJoin:
    def __init__(
        self,
        left_statement: Union[Self, Statement],
        right_statement: Union[Self, Statement],
        left_path: list[str],
        right_path: list[str],
        join_function: Callable = ExactOrIn,
    ):
        self.left_statement = left_statement
        self.right_statement = right_statement
        self.join_function = join_function

        self.left_path = left_path
        self.right_path = right_path

    def __call__(self, collection: PanosObjectCollection):
        joined_objects = []
        left = self.left_statement(collection)
        right = self.right_statement(collection)
        for left_obj in left:
            left_value = get_value_recursive(left_obj, self.left_path)
            for right_obj in right:
                right_value = get_value_recursive(right_obj, self.right_path)
                if self.join_function(left_value)(right_value):
                    left_obj.add_joined_object(right_obj)
                    right_obj.add_joined_object(left_obj)
                    joined_objects.append(right_obj)

        return joined_objects
