import json
from pyramid.response import Response
from pyramid.view import view_config

from sqlalchemy.exc import DBAPIError

from .models import (
    DBSession,
    Poll,
    Choice,
    Response
    )

import logging
LOG = logging.getLogger(__name__)

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
