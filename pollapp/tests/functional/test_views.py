from base import BaseTestCase

class TestViews(BaseTestCase):

    def test_create_poll_successful(self):
        r = self.create_poll(self.name,
            self.options_str)
        self.assertEqual(r.status_code, 200)
        self.assertEqual("id" in r.json(), True)
        self.assertEqual(r.json()["id"] is not None, True)

    def test_vote_chocie1(self):
        r1 = self.create_poll(self.name,
            self.options_str)
        self.assertEqual(r1.status_code, 200)
        poll_id = r1.json()["id"]
        choice_index = 0
        r2 = self.create_vote(poll_id, choice_index,
            self.ip_address)
        self.assertEqual(r2.status_code, 200)
        self.assertEqual(r2.json()["status"], "Ok")
