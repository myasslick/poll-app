import os
import random
import unittest
from contextlib import contextmanager

import json
import requests
import subprocess
import time
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
HOSTNAME = "http://localhost:9876"
POLL_URL = HOSTNAME + "/polls"

# Before we proceed, ensure testing.ini exists.
if not os.path.exists(TEST_INI):
    sys.exit(" ".join([TEST_INI, "must be present to run functional tests."]))

def random_ip():
    return "{}.{}.{}.{}".format(
        random.randint(0, 255),
        random.randint(0, 255),
        random.randint(0, 255),
        random.randint(0, 255)
    )

def get_pserve_path():
    p = subprocess.Popen(["which", "pserve"], stdout=subprocess.PIPE)
    out, err = p.communicate()
    return out

def start_server():
    pserve = get_pserve_path()
    if not pserve:
        sys.exit("Incorrect environment. pserve not found.")
    p = subprocess.Popen([pserve.strip(), TEST_INI],
                         stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE)
    time.sleep(3)
    return p

def make_vote_url(poll_id):
    return "/".join([POLL_URL, poll_id, "vote"])

def make_result_url(poll_id):
    return "/".join([POLL_URL, poll_id, "results"])

class BaseTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        settings = appconfig('config:' + TEST_INI)
        cls.engine = engine_from_config(settings, prefix='sqlalchemy.')
        cls.session = sessionmaker(bind=cls.engine)()
        models.Base.metadata.create_all(cls.engine, checkfirst=True)
        transaction.commit()

        cls.name = "Yay or Nay?"
        cls.options = [
            "Yay",
            "Nay",
            "Maybe"
        ]
        cls.options_str = ",".join(cls.options)

        cls.server = start_server()

    @classmethod
    def tearDownClass(cls):
        models.Base.metadata.drop_all(cls.engine)
        cls.session.close_all()
        cls.engine.dispose()
        cls.server.terminate()
        cls.server.kill()
        time.sleep(1)

    def setUp(self):
        self.ip_address = random_ip()
        self.session = (
            scoped_session(sessionmaker(
                extension=ZopeTransactionExtension()
                )
            )
        )

    def create_poll(self, name, options_str):
        data = {
            "name": name,
            "options": options_str
        }
        headers = {"content-type": "application/json"}
        r = requests.post(POLL_URL, data=json.dumps(data),
            headers=headers)
        return r

    def create_vote(self, poll_id, option_index, ip_address):
        data = {
            "option": option_index,
            "ip": ip_address
        }
        headers = {"content-type": "application/json"}
        vote_url = make_vote_url(poll_id)
        r = requests.post(vote_url, data=json.dumps(data),
            headers=headers)
        return r

    def get_result(self, poll_id):
        result_url = make_result_url(poll_id)
        r = requests.get(result_url)
        return r
