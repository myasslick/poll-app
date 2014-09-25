from pyramid.view import view_config

from ..models import (
    DBSession,
    Poll,
    Choice,
    )

from .. import validation
from ..validation import validator
from .base import DefaultView

import logging
LOG = logging.getLogger(__name__)

POST = "POST"

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
