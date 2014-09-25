from base import BaseTestCase

class TestModelIntegration(BaseTestCase):
    def test_create_poll(self):
        poll = self.create_poll()
        with self.on_session([poll]):
            self.assertEqual(poll.name, self.name)

    def test_create_choice(self):
        poll = self.create_poll()
        choice = self.create_choice(self.options[0])
        choice.poll = poll
        with self.on_session([poll, choice]):
            self.assertEqual(choice.text, self.options[0])
            self.assertEqual(choice.poll, poll)

    def test_create_response(self):
        poll = self.create_poll()
        choice = self.create_choice(self.options[0])
        response = self.create_response()
        response.choice = choice
        choice.poll = poll
        with self.on_session([poll, choice, response]):
            self.assertEqual(response.choice, choice)
