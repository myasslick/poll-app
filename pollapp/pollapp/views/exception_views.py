from pyramid.view import view_config
from ..exceptions import (
    HTTPNotFoundError,
    ValidationError
    )

import logging
LOG = logging.getLogger(__name__)

@view_config(context=Exception, renderer='json')
def http_500_uncaught_internal_error(exc, request):
    LOG.error("Unhandled 500 error and stacktrace: ======")
    LOG.exception(exc)
    request.response.status_code = 500
    body = {
        "message": "500 Internal Server Error",
        "status": "error"
    }
    return body

@view_config(context=HTTPNotFoundError, renderer='json')
def http_404_not_found(exc, request):
    """ The resource which the request party is seeking
    is not found. Developers are free to use 404
    instead of 403 to indicate resource not found
    so no accidental information leakage (e.g. an
    authenticated user tried to see someone else's
    exercise but receives 404 knows nothing about
    the existence of the tried exercise). """

    request.response.status_code = 404
    return {
        "status": "fail",
        "error": {"type": "not_found"},
        "message": exc.msg
    }

@view_config(context=ValidationError, renderer='json')
def http_400_bad_request(exc, request):
    """ The resource cannot be completed because the
    request either contains malformed request body,
    or did not pass the request validation. """

    LOG.info("400 error " + exc.message)
    request.response.status_code = 400
    body = {
        "status": "fail",
        "error": {
            "field": exc.field,
            "type": exc.type,
            "value": exc.value
        },
        "message": exc.msg,
    }
    return body
