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
from .validation import validator

import logging
LOG = logging.getLogger(__name__)

GET = "GET"
POST = "POST"

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

@view_config(route_name="vote", renderer="json", request_method="POST")
def vote(request):
    poll_id = request.matchdict["id"]
    LOG.info("Poll id requested: " + str(poll_id))

    poll = DBSession.query(Poll).filter_by(_id=poll_id).first()
    LOG.info("Poll exist: " + str(poll is not None))
    if poll:
        index = int(request.json_body["option"])
        ip_address = request.json_body["ip"]
        resp = Response(ip_address=ip_address)
        resp.choice = poll.choices[index]
        DBSession.add(resp)
        return {"status": "Ok"}

@view_config(route_name="results", renderer="json", request_method="GET")
def get_result(request):
    poll_id = request.matchdict["id"]
    poll = DBSession.query(Poll).filter_by(_id=poll_id).first()
    if poll:
        return get_counts(poll.id)
