class ExactOrIn:
    """Exact match, or if the provided value is a list, if the value appears exactly in the list."""

    def __init__(self, match):
        self.match = match

    def __call__(self, value):
        if isinstance(value, list):
            if self.match in value:
                return True

            return False
        else:
            if self.match == value:
                return True


class MatchInListOfObjectAttributes:
    """Matches when the given attribute is the same between two collections of objects

    This works by flattening the given match collection at the provided path, producing a list of match critera
    """

    def __init__(
        self, match_collection, match_path: list[str], match_function=ExactOrIn
    ):
        self.match_collection = match_collection
        self.match_path = match_path
        self.match_function = match_function


    def __call__(self, collection):
        pass
