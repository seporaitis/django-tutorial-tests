from django.http import Http404
from django.utils import timezone
from django.urls import reverse

from polls.models import Choice, Question
from polls.tests import base
from polls.views import DetailView, IndexView, ResultsView, vote


class QuestionViewTests(base.BaseTestCase):

    def test_index_view_with_no_questions(self):
        """
        If no questions exist, an appropriate message should be displayed.
        """
        request = self.request_factory.get(reverse('polls:index'))
        response = IndexView.as_view()(request)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No polls are available")

    def test_index_view_with_a_past_question(self):
        """
        Questions with a pub_date in the past should be displayed on the
        index page.
        """
        question = self.create_question(question_text="Past question", days=-30)
        request = self.request_factory.get(reverse('polls:index'))
        response = IndexView.as_view()(request)

        self.assertContains(response, question.question_text)

    def test_index_view_with_a_future_question(self):
        """
        Questions with a pub_date in the future should not be displayed on
        the index page.
        """
        question = self.create_question(question_text="Future question", days=30)
        request = self.request_factory.get(reverse('polls:index'))
        response = IndexView.as_view()(request)

        self.assertNotContains(response, question.question_text)

    def test_index_view_with_future_question_and_past_question(self):
        """
        Even if both past and future questions exist, only past questions
        should be displayed.
        """
        past_question = self.create_question(question_text="Past question", days=-30)
        future_question = self.create_question(question_text="Future question", days=30)
        request = self.request_factory.get(reverse('polls:index'))
        response = IndexView.as_view()(request)

        self.assertContains(response, past_question.question_text)
        self.assertNotContains(response, future_question.question_text)

    def test_index_view_with_two_past_questions(self):
        """
        The questions index page may display multiple questions.
        """
        question1 = self.create_question(question_text="Past question", days=-30)
        question2 = self.create_question(question_text="Past question", days=-5)
        request = self.request_factory.get(reverse('polls:index'))
        response = IndexView.as_view()(request)

        self.assertContains(response, question1.question_text)
        self.assertContains(response, question2.question_text)


class QuestionIndexDetailsTests(base.BaseTestCase):

    def test_detail_view_with_a_future_question(self):
        """
        The detail view of a question with a pub_date in the future should
        return a 404 not found.
        """
        future_question = self.create_question(question_text='Future question.', days=5)
        request = self.request_factory.get(reverse('polls:detail', args=(future_question.id,)))
        with self.assertRaises(Http404):
            DetailView.as_view()(request, pk=future_question.id)


    def test_detail_view_with_a_past_question(self):
        """
        The detail view of a question with a pub_date in the past should
        display the question's text.
        """
        past_question = self.create_question(question_text='Past Question.', days=-5)
        request = self.request_factory.get(reverse('polls:detail', args=(past_question.id,)))
        response = DetailView.as_view()(request, pk=past_question.id)
        self.assertContains(response, past_question.question_text)


class QuestionResultsTests(base.BaseTestCase):

    def test_results_empty(self):
        """
        The results view of a question should display choices and counts.
        """
        question = self.create_question(question_text='Question.', days=-5)
        choice1 = Choice.objects.create(
            question=question,
            choice_text='Choice 1',
            votes=10,
        )
        choice2 = Choice.objects.create(
            question=question,
            choice_text='Choice 2',
            votes=11,
        )

        request = self.request_factory.get(reverse('polls:results', args=(question.id,)))
        response = ResultsView.as_view()(request, pk=question.id)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "<li>{} -- {} votes</li>".format(choice1.choice_text, choice1.votes))
        self.assertContains(response, "<li>{} -- {} votes</li>".format(choice2.choice_text, choice2.votes))



class VoteTests(base.BaseTestCase):

    def setUp(self):
        super().setUp()

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

    def test_view(self):
        url = reverse('polls:vote', args=(self.question.id,))
        request = self.request_factory.post(url, {'choice': self.choice2.id})
        response = vote(request, self.question.id)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('polls:results', args=(self.question.id,)))
