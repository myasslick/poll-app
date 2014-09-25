import json
from pyramid.response import Response
from pyramid.view import view_config

from sqlalchemy.exc import DBAPIError
from sqlalchemy.sql import text

from .models import (
    DBSession,
    Poll,
    Choice,
    Response
    )

import logging
LOG = logging.getLogger(__name__)

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

@view_config(route_name="polls", renderer="json", request_method="POST")
def create_poll(request):
    name = request.json_body["name"]
    options = request.json_body["options"].split(",")
    poll = Poll(name=name)
    choices = [Choice(text=option) for option in options]
    for choice in choices:
        poll.choices.append(choice)
    DBSession.add(poll)
    DBSession.add_all(choices)
    return {"id": poll._id}

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
