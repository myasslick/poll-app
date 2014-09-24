from base import BaseTestCase

class TestViews(BaseTestCase):

    def test_create_poll_successful(self):
        r = self.create_poll(self.question,
            self.options_str)
        self.assertEqual(r.status_code, 200)
        self.assertEqual("id" in r.json(), True)
