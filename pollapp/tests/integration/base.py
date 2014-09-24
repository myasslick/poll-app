import os
import unittest
from contextlib import contextmanager

import transaction
from pyramid import testing
from sqlalchemy import engine_from_config
from paste.deploy.loadwsgi import appconfig
from sqlalchemy.orm import sessionmaker
from zope.sqlalchemy import ZopeTransactionExtension
from sqlalchemy.orm import scoped_session

from pollapp import models

TEST_DIR = os.path.abspath(
        os.path.dirname(
            os.path.dirname(__file__)
           )
        )

CONFIG_DIR = os.path.join(TEST_DIR, "configurations")

TEST_INI = os.path.join(CONFIG_DIR, "testing.ini")

# Let's finish setting up all the tests...
# Most annoying and tedious part :(

class BaseTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        settings = appconfig('config:' + TEST_INI)
        cls.engine = engine_from_config(settings, prefix='sqlalchemy.')
        models.Base.metadata.tables["poll"].create(bind=cls.engine)
        models.Base.metadata.tables["choice"].create(bind=cls.engine)
        models.Base.metadata.tables["response"].create(bind=cls.engine)
        transaction.commit()

        cls.name = "Yay or Nay?"
        cls.options = [
            "Yay",
            "Nay"
        ]
        cls.ip_address = "192.168.1.1"

    @classmethod
    def tearDownClass(cls):
        models.Base.metadata.drop_all(cls.engine)

    def setUp(self):
        #self.session = (
        #    scoped_session(sessionmaker(
        #        extension=ZopeTransactionExtension()
        #        )
        #    )
        #)
        self.Session = sessionmaker(bind=self.engine)
        self.session = self.Session()

    def tearDown(self):
        self.session.rollback()

    @contextmanager
    def on_session(self, insts):
        for inst in insts:
            self.session.add(inst)
            self.session.flush()
            self.session.refresh(inst)
        yield

    def create_poll(self, name=None):
        return models.Poll(name=name
            or self.name)

    def create_choice(self, text):
        return models.Choice(text=text)

    def create_response(self, ip_address=None):
        return models.Response(ip_address=ip_address
            or self.ip_address)
