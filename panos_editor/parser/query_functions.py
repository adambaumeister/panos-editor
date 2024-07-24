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
