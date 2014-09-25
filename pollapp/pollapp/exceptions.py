class ValidationError(Exception):
    def __init__(self, type, field, msg, value=None):
        super(ValidationError, self).__init__(msg)
        self.type = type
        self.field = field
        self.msg = msg
        self.value = value

class MissingFieldError(ValidationError):
    """ Required field is missing from the request body. """
    def __init__(self, field, msg):
        super(MissingFieldError, self).__init__(
            "missing_field", field, msg)

class InvalidFieldValueError(ValidationError):
    """ Raises this error if an unknown field
    is found in the request body.

    """
    def __init__(self, field, msg, value=None):
        super(InvalidFieldValueError, self).__init__(
            "invalid", field, msg, value=value)
