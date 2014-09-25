from pyramid.view import view_config
from sqlalchemy.sql import text

from ..models import (
    DBSession,
    Poll
    )

from .base import DefaultView
from .. import validation
from ..exceptions import HTTPNotFoundError
from ..validation import validator

import logging
LOG = logging.getLogger(__name__)

GET = "GET"

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

@view_config(route_name="results", renderer="json", request_method="GET")
def get_result(request):
    poll_id = request.matchdict["id"]
    poll = DBSession.query(Poll).filter_by(_id=poll_id).first()
    if poll:
        return get_counts(poll.id)
    else:
        raise HTTPNotFoundError()
