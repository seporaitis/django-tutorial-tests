import datetime

from django.utils import timezone
from django.test import TestCase, RequestFactory

from polls.models import Question


class BaseTestCase(TestCase):

    def setUp(self):
        super().setUp()

        self.request_factory = RequestFactory()

    def create_question(self, question_text, days):
        """
        Creates a question with the given `question_text` and published the
        given number of `days` offset to now (negative for questions published
        in the past, positive for questions that have yet to be published).
        """
        time = timezone.now() + datetime.timedelta(days=days)
        return Question.objects.create(question_text=question_text, pub_date=time)
