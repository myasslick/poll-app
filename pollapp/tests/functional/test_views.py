from base import BaseTestCase

class TestViews(BaseTestCase):

    def assert_result_response_keys(self, resp):
        for r in resp.json():
            keys = r.keys()
            expected = ("name", "unique_votes", "votes")
            self.assertEqual(len(keys), len(expected))
            for e in expected:
                self.assertTrue(e in keys)

    def assert_result_response_length_and_keys(self, resp, options):
        self.assertEqual(len(options), len(resp.json()))
        self.assert_result_response_keys(resp)

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
        self.assertEqual(r2.json()["status"], u"Ok")

    def test_get_result_with_zeros(self):
        r1 = self.create_poll(self.name,
            self.options_str)
        poll_id = r1.json()["id"]

        r2 = self.get_result(poll_id)
        self.assertEqual(r2.status_code, 200)
        self.assert_result_response_length_and_keys(r2, self.options)
        for i, option in enumerate(self.options):
            self.assertEqual(r2.json()[i]["name"], option)
            self.assertEqual(r2.json()[i]["unique_votes"], 0)
            self.assertEqual(r2.json()[i]["votes"], 0)

    def test_two_distinct_votes(self):
        r1 = self.create_poll(self.name,
            self.options_str)
        poll_id = r1.json()["id"]
        r2 = self.create_vote(poll_id, 0, self.ip_address)
        self.assertEqual(r2.status_code, 200)
        r3 = self.create_vote(poll_id, 1, self.ip_address)
        self.assertEqual(r3.status_code, 200)

        voted_indices = (0,1)
        r4 = self.get_result(poll_id)
        self.assertEqual(r4.status_code, 200)
        self.assert_result_response_length_and_keys(r4, self.options)
        for i in voted_indices:
            self.assertEqual(r4.json()[i]["name"], self.options[i])
            self.assertEqual(r4.json()[i]["unique_votes"], 1)
            self.assertEqual(r4.json()[i]["votes"], 1)
        else:
            # But the last option remains zero
            i += 1
            self.assertEqual(r4.json()[i]["name"], self.options[i])
            self.assertEqual(r4.json()[i]["unique_votes"], 0)
            self.assertEqual(r4.json()[i]["votes"], 0)

    def test_index1_gets_two_duplicates(self):
        r1 = self.create_poll(self.name,
            self.options_str)
        poll_id = r1.json()["id"]
        r2 = self.create_vote(poll_id, 1, self.ip_address)
        self.assertEqual(r2.status_code, 200)
        r3 = self.create_vote(poll_id, 1, self.ip_address)
        self.assertEqual(r3.status_code, 200)

        r4 = self.get_result(poll_id)
        self.assertEqual(r4.status_code, 200)
        self.assert_result_response_length_and_keys(r4, self.options)
        self.assertEqual(r4.json()[1]["name"], self.options[1])
        self.assertEqual(r4.json()[1]["unique_votes"], 1)
        self.assertEqual(r4.json()[1]["votes"], 2)
