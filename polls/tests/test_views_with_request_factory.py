from django.utils import timezone
from django.urls import reverse
from django.test import TestCase, RequestFactory

from polls.models import Choice, Question
from polls.views import vote


class VoteTests(TestCase):

    def setUp(self):
        super().setUp()

        self.request_factory = RequestFactory()

        self.question = Question.objects.create(
            question_text='Is this a test?',
            pub_date=timezone.now()
        )
        self.question.save()

        self.choice1 = Choice(
            question=self.question,
            choice_text='No',
            votes=0,
        )
        self.choice1.save()

        self.choice2 = Choice(
            question=self.question,
            choice_text='Yes',
            votes=0,
        )
        self.choice2.save()

    def test_vote(self):
        url = reverse('polls:vote', args=(self.question.id,))
        request = self.request_factory.post(url, {'choice': self.choice2.id})
        response = vote(request, self.question.id)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('polls:results', args=(self.question.id,)))
