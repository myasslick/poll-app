from base import BaseTestCase

class TestModelIntegration(BaseTestCase):
    def test_create_poll(self):
        poll = self.create_poll()
        with self.on_session([poll]):
            self.assertEqual(poll.question, self.question)

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

"""
class TestMyViewSuccessCondition(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()
        from sqlalchemy import create_engine
        engine = create_engine('sqlite://')
        from .models import (
            Base,
            MyModel,
            )
        DBSession.configure(bind=engine)
        Base.metadata.create_all(engine)
        with transaction.manager:
            model = MyModel(name='one', value=55)
            DBSession.add(model)

    def tearDown(self):
        DBSession.remove()
        testing.tearDown()

    def test_passing_view(self):
        from .views import my_view
        request = testing.DummyRequest()
        info = my_view(request)
        self.assertEqual(info['one'].name, 'one')
        self.assertEqual(info['project'], 'pollapp')


class TestMyViewFailureCondition(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()
        from sqlalchemy import create_engine
        engine = create_engine('sqlite://')
        from .models import (
            Base,
            MyModel,
            )
        DBSession.configure(bind=engine)

    def tearDown(self):
        DBSession.remove()
        testing.tearDown()

    def test_failing_view(self):
        from .views import my_view
        request = testing.DummyRequest()
        info = my_view(request)
        self.assertEqual(info.status_int, 500)
"""
