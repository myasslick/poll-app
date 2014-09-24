import unittest
try:
    from unittest.mock import MagicMock, patch, call
except ImportError:
    from mock import MagicMock, patch, call

from pollapp import models

class TestModelsUnittests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.question = "Yay or Nay?"
        cls.options = [
            "Yay",
            "Nay"
        ]
        cls.ip_address = "192.168.1.1"

    def create_poll(self, question=None):
        return models.Poll(question=question
            or self.question)

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

    def test_create_poll(self):
        poll = self.create_poll()
        self.assertEqual(poll.question, self.question)

    def test_create_choice(self):
        choice = self.create_choice(self.options[0])
        self.assertEqual(choice.text, self.options[0])

    def test_create_response(self):
        response = self.create_response()
        self.assertEqual(response.ip_address, self.ip_address)

    def test_append_options_to_poll(self):
        poll, choice1, choice2 = self.create_choices()
        self.assertEqual(poll.choices.all(), [])
        # Now append choice 1 and 2 to poll
        poll.choices.append(choice1)
        poll.choices.append(choice2)
        self.assertEqual(len(poll.choices.all()), 2)
        self.assertEqual(poll.choices[0], choice1)
        self.assertEqual(poll.choices[1], choice2)

    def test_response_made_for_choice1(self):
        poll, choice1, choice2 = self.create_and_append_choices()
        response = self.create_response()
        self.assertEqual(response.choice, None)
        response.choice = choice1
        self.assertEqual(response.choice, choice1)
