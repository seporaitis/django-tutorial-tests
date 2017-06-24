import datetime

from django.contrib.auth.models import User
from django.utils import timezone
from django.urls import reverse
from django.test import TestCase, RequestFactory

from polls.models import Choice, Question
from polls.views import ResultsView, vote


def create_question(question_text, days):
    """
    Creates a question with the given `question_text` and published the
    given number of `days` offset to now (negative for questions published
    in the past, positive for questions that have yet to be published).
    """
    time = timezone.now() + datetime.timedelta(days=days)
    return Question.objects.create(question_text=question_text, pub_date=time)


class QuestionViewTests(TestCase):
    def test_index_view_with_no_questions(self):
        """
        If no questions exist, an appropriate message should be displayed.
        """
        response = self.client.get(reverse('polls:index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No polls are available.")
        self.assertQuerysetEqual(response.context['latest_question_list'], [])

    def test_index_view_with_a_past_question(self):
        """
        Questions with a pub_date in the past should be displayed on the
        index page.
        """
        create_question(question_text="Past question.", days=-30)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(
            response.context['latest_question_list'],
            ['<Question: Past question.>']
        )

    def test_index_view_with_a_future_question(self):
        """
        Questions with a pub_date in the future should not be displayed on
        the index page.
        """
        create_question(question_text="Future question.", days=30)
        response = self.client.get(reverse('polls:index'))
        self.assertContains(response, "No polls are available.")
        self.assertQuerysetEqual(response.context['latest_question_list'], [])

    def test_index_view_with_future_question_and_past_question(self):
        """
        Even if both past and future questions exist, only past questions
        should be displayed.
        """
        create_question(question_text="Past question.", days=-30)
        create_question(question_text="Future question.", days=30)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(
            response.context['latest_question_list'],
            ['<Question: Past question.>']
        )

    def test_index_view_with_two_past_questions(self):
        """
        The questions index page may display multiple questions.
        """
        create_question(question_text="Past question 1.", days=-30)
        create_question(question_text="Past question 2.", days=-5)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(
            response.context['latest_question_list'],
            ['<Question: Past question 2.>', '<Question: Past question 1.>']
        )


class QuestionIndexDetailTests(TestCase):
    def test_detail_view_with_a_future_question(self):
        """
        The detail view of a question with a pub_date in the future should
        return a 404 not found.
        """
        future_question = create_question(question_text='Future question.', days=5)
        url = reverse('polls:detail', args=(future_question.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_detail_view_with_a_past_question(self):
        """
        The detail view of a question with a pub_date in the past should
        display the question's text.
        """
        past_question = create_question(question_text='Past Question.', days=-5)
        url = reverse('polls:detail', args=(past_question.id,))
        response = self.client.get(url)
        self.assertContains(response, past_question.question_text)


class VoteTests(TestCase):

    def setUp(self):
        super().setUp()

        self.request_factory = RequestFactory()

        self.question = create_question(question_text='Some question.', days=0)
        self.question.save()

        self.choice1 = Choice(
            question=self.question,
            choice_text='Choice 1',
            votes=0,
        )
        self.choice1.save()

        self.choice2 = Choice(
            question=self.question,
            choice_text='Choice 2',
            votes=0,
        )
        self.choice2.save()

    def test_vote_counts_with_client(self):
        url = reverse('polls:vote', args=(self.question.id,))
        # follow=True follows the redirect chain so response is the end page
        response = self.client.post(url, {'choice': self.choice2.id}, follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "<li>{} -- 0 votes</li>".format(self.choice1.choice_text))
        self.assertContains(response, "<li>{} -- 1 vote</li>".format(self.choice2.choice_text))

    def test_post_redirect_with_client(self):
        url = reverse('polls:vote', args=(self.question.id,))
        response = self.client.post(url, {'choice': self.choice2.id})

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['Location'], reverse('polls:results', args=(self.question.id,)))

    def test_logged_in_redirect(self):
        # This test is no different from test_post_redirect, but it
        # shows an example with logging in before calling `post`.
        password = 'test'
        user = User(username='test')
        user.set_password(password)
        user.save()

        logged_in = self.client.login(username=user.username, password=password)
        self.assertTrue(logged_in)

        url = reverse('polls:vote', args=(self.question.id,))
        response = self.client.post(url, {'choice': self.choice2.id})

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['Location'], reverse('polls:results', args=(self.question.id,)))
