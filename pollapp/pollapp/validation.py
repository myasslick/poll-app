from functools import wraps
from pyramid.response import Response
from .exceptions import (ValidationError,
    MissingFieldError, InvalidFieldValueError)
import logging
LOG = logging.getLogger(__name__)

def validator(verify_func):
    """ Decorates a view function and perform per-view
    specific input validation.

    Args:
        verify_func: Pass the function to this validator
            so the validator will call the function to
            validate the input data.

    Returns:
        At the end the view function context is returned
        and calls the view function with the request.
    """

    def decorator(view_func):
        @wraps(view_func)
        def wrapper(cls):
            if cls.request.method == "POST":
                data = cls.request.json_body
                cleaned = verify_func(data)
                setattr(cls.request, "cleaned_data", cleaned)
            return view_func(cls)
        return wrapper
    return decorator

def has_required_fields(required_fields, actual_fields):
    """ Checks if input data contains all the required
    fields.

    Args:
        required_fields: A list of required fields
            input must have.
        actual_fields: A list of the fields present
            in the input. This is usually the keys
            of the input data.

    Returns:
        Returns ``True`` if all fields are present
        or ``False`` if at least one field is missing.
    """
    for field in required_fields:
        if field not in actual_fields:
            raise MissingFieldError(field,
                "Missing required field: %s" % field)

def check_create_poll(data):
    expected_fields = ("name", "options")
    has_required_fields(expected_fields, data.keys())

    # options cannot be an empty string. There must
    # be at least 1 non-empty string
    splited = data["options"].split(",")
    if splited:
        return {"name": data["name"], "options": splited}
    else:
        raise InvalidFieldValueError("options",
            "Must be a non-empty string. Multiple options must be\
separated by comma.", value=data["options"])
