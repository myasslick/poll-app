from pyramid.view import view_config

from ..models import (
    DBSession,
    Poll,
    Choice,
    Response
    )

from .base import DefaultView
from .. import validation
from ..exceptions import HTTPNotFoundError
from ..validation import validator

import logging
LOG = logging.getLogger(__name__)

POST = "POST"

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
