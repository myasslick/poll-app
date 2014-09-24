from pyramid.config import Configurator
from sqlalchemy import engine_from_config

from .models import (
    DBSession,
    Base,
    )


def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    engine = engine_from_config(settings, "sqlalchemy.")
    DBSession.configure(bind=engine)
    Base.metadata.bind = engine
    config = Configurator(settings=settings)
    config.include("pyramid_chameleon")
    config.add_route("polls", "/polls")
    config.add_route("vote", "/polls/{id}/vote")
    config.add_route("results", "/polls/{id}/results")
    config.scan()
    return config.make_wsgi_app()
