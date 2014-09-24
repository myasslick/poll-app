import os
import unittest
from contextlib import contextmanager

import transaction
import unittest
from pollapp import models

TEST_DIR = os.path.abspath(
        os.path.dirname(
            os.path.dirname(__file__)))

CONFIG_DIR = os.path.join(TEST_DIR, "configurations")

TEST_INI = os.path.join(CONFIG_DIR, "testing.ini")

# Let's finish setting up all the tests...
# Most annoying and tedious part :(

class BaseTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.name = "Yay or Nay?"
        cls.options = [
            "Yay",
            "Nay"
        ]
        cls.ip_address = "192.168.1.1"

    def create_poll(self, name=None):
        return models.Poll(name=name
            or self.name)

    def create_choice(self, text):
        return models.Choice(text=text)

    def create_response(self, ip_address=None):
        return models.Response(ip_address=ip_address
            or self.ip_address)
 
    def create_choices(self):
        poll = self.create_poll()
        choice1 = self.create_choice(self.options[0])
        choice2 = self.create_choice(self.options[1])
        return poll, choice1, choice2

    def create_and_append_choices(self):
        poll, choice1, choice2 = self.create_choices()
        poll.choices.append(choice1)
        poll.choices.append(choice2)
        return poll, choice1, choice2
