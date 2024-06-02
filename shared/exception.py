class ParsingException(Exception):
    def __init__(self, message):
        super().__init__(message)


class EmptyDescriptionException(Exception):
    def __init__(self, message):
        super().__init__(message)
