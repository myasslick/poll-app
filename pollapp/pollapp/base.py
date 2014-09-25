from pyramid.view import view_defaults

class DefaultView(object):
    """Base class for all views.

    Every view class inherits from this base class should
    define ``__init__`` method which takes a single
    argument: ``request``. The ``__init__`` should
    set the ``request`` instance to the new attribute
    ``self.request``.

    Also, every view method (the method that actually
    runs the views) should be decorated with
    :func:`pyramid.view.view_config` and should at least
    sets the view's ``request_method``. Pyramid will
    inspect classes and their methods to discover routes
    if they are decorated by :func:`pyramid.view.view_defaults`
    and :func:`pyramid.view.view_config`.

    This base class is **not** decorated with
    :func:`pyramid.view.view_defaults` so the classes that
    inherit can define a renderer either via
    :func:`pyramid.view.view_defaults` (at class level)
    or :func:`pyramid.view.view_config` (at method or
    function level). If no explicit renderer is defined
    for a view, the response will be returned as
    ``text/html``. :meth:`.success`, :meth:`.error`
    and :meth:`.fail` works by returning the body
    to the renderer; so unless ``renderer="json"``
    is set expliclity, calling one of the response
    methods will not send the response data as JSON.
    """

    def success(self, status_code, data=None, message=None,
        override=False):
       """Returns a 2xx range response.

        Args:
            status_code: the response status code (2xx)
            data: data to return to user in dictionary (default: ``None``)
            message: custom message to return (default: ``"Ok"``)
            override: whether to return data directly or use the standard
                format (default: ``False``)
        Returns:
            Returns the body to be rendered.
        """
        self.request.response.status_code = status_code
        if override:
            return data
        else:
            body = {
                "status": "success",
                "data": data,
                "message": message or "Ok"
            }

    def error(self, status_code, error=None, message=None):
        """Returns a 5xx range response.

        Args:
            status_code: the response status code (5xx)
            error: a dictionary contains error (default: ``None``)
            message: custom message to return (default: ``None``)

        Returns:
            Returns the body to be rendered.
        """
        self.request.response.status_code = status_code
        body = {
            "status": "error",
            "error": error,
            "message": message
        }
        return body

    def fail(self, status_code, error=None, data=None, message=None):
        """Returns a 4xx range response.

        Args:
            status_code: the response status code (4xx)
            error: a dictionary contains error (default: ``None``)
            data: a dictionary contains necessary data to return
                (default: ``None``)
            message: custom message to return (default: ``None``)

        Returns:
            Returns the body to be rendered.
        """
        self.request.response.status_code = status_code
        body = {
            "status": "fail",
            "error": error,
            "message": message,
            "data": data
        }
        return body
