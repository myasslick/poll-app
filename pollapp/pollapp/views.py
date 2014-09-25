import json
from pyramid.response import Response
from pyramid.view import view_config, view_defaults

from sqlalchemy.exc import DBAPIError
from sqlalchemy.sql import text

from .models import (
    DBSession,
    Poll,
    Choice,
    Response
    )

from . import validation
from .base import DefaultView
from .exceptions import HTTPNotFoundError, ValidationError
from .validation import validator

import logging
LOG = logging.getLogger(__name__)

GET = "GET"
POST = "POST"

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

def get_counts(poll_id):
    params = {"poll_id": poll_id}
    query = text("""\
SELECT choice.id,
       choice.text,
       Count(DISTINCT response.ip_address) AS unique_count,
       Count(response.ip_address) AS raw_count
FROM choice
LEFT OUTER JOIN response ON response.choice_id = choice.id
WHERE choice.poll_id = :poll_id
GROUP BY choice.id;
""")
    result = DBSession.execute(query, params)
    if result:
        return [{"name": r.text,
                 "votes": r.raw_count,
                 "unique_votes": r.unique_count}
                for r in result.fetchall()]
    else:
        return []

def create_poll(session, name, options):
    poll = Poll(name=name)
    choices = [Choice(text=option) for option in options]
    for choice in choices:
        poll.choices.append(choice)
    session.add(poll)
    session.add_all(choices)
    return poll

class PollViews(DefaultView):
    def __init__(self, request):
        self.request = request

    @view_config(route_name="polls", renderer="json", request_method=POST)
    @validator(validation.check_create_poll)
    def create_poll(self):
        name = self.request.cleaned_data["name"]
        options = self.request.cleaned_data["options"]
        poll = create_poll(DBSession, name, options)
        return self.success(201, override=True,
            data={"id": poll._id}
        )

class VoteViews(DefaultView):
    def __init__(self, request):
        self.request = request

    def get_poll_or_404(self, session, poll_id):
        LOG.debug("Searching for poll id: " + poll_id)
        poll = DBSession.query(Poll).filter_by(_id=poll_id).first()
        LOG.debug("Poll exist: " + str(poll is not None))
        if not poll:
            raise HTTPNotFoundError()
        return poll

    def cast_vote(self, session, poll, option, ip_address):
        resp = Response(ip_address=ip_address)
        resp.choice = poll.choices[option]
        session.add(resp)

    @view_config(route_name="vote", renderer="json", request_method=POST)
    @validator(validation.check_vote)
    def vote(self):
        poll_id = self.request.matchdict["id"]
        LOG.info("Poll id requested: " + str(poll_id))

        poll = self.get_poll_or_404(DBSession, poll_id)

        option = self.request.cleaned_data["option"]
        ip_address = self.request.cleaned_data["ip"]
        try:
            self.cast_vote(DBSession, poll, option, ip_address)
            return self.success(201, override=True,
                data={"status": u"Ok"})
        except IndexError:
            return self.fail(409, error="invalid-option",
                message="The option index is out of range.")

@view_config(route_name="results", renderer="json", request_method="GET")
def get_result(request):
    poll_id = request.matchdict["id"]
    poll = DBSession.query(Poll).filter_by(_id=poll_id).first()
    if poll:
        return get_counts(poll.id)
    else:
        raise HTTPNotFoundError()
