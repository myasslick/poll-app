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
    question = request.json_body["name"]
    options = request.json_body["options"].split(",")
    poll = Poll(question=question)
    choices = [Choice(text=option) for option in options]
    for choice in choices:
        poll.choices.append(choice)
    DBSession.add(poll)
    DBSession.add_all(choices)
    return {"id": poll.id}
