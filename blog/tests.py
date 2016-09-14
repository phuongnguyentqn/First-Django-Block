import datetime
from django.test import TestCase
from django.utils import timezone
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404

from .models import Question, Choice

class PollTestCase(TestCase):
    fixtures = ['form_testdata.json']

    def setUp(self):
        super(PollTestCase, self).setUp()
        self.poll_1 = Question.objects.get(pk=1)
        self.poll_2 = Question.objects.get(pk=2)

    def test_was_published_today(self):
        # Because unless you're timetraveling, they weren't.
        self.assertFalse(self.poll_1.was_published_recently())
        self.assertFalse(self.poll_2.was_published_recently())

        # Modify & check again.
        now = datetime.datetime.now()
        self.poll_1.pub_date = now
        self.poll_1.save()
        self.assertTrue(self.poll_1.was_published_recently())

    def test_no_future_dated_polls(self):
        # Create the future-dated ``Poll``.
        poll = Question.objects.create(
            question_text="Do we have flying cars yet?",
            pub_date=datetime.datetime.now() + datetime.timedelta(days=1)
        )
        self.assertEqual(
            list(Question.objects.all().values_list('id', flat=True)),
            [1, 2, 3]
        )

class ChoiceTestCase(TestCase):
    fixtures = ['form_testdata.json']

    def test_record_vote(self):
        choice_1 = Choice.objects.get(pk=1)
        choice_2 = Choice.objects.get(pk=2)
        self.assertEqual(Choice.objects.get(pk=1).votes, 1)
        self.assertEqual(Choice.objects.get(pk=2).votes, 0)

        choice_1.record_vote()
        self.assertEqual(Choice.objects.get(pk=1).votes, 2)
        self.assertEqual(Choice.objects.get(pk=2).votes, 0)

        choice_2.record_vote()
        self.assertEqual(Choice.objects.get(pk=1).votes, 2)
        self.assertEqual(Choice.objects.get(pk=2).votes, 1)

        choice_1.record_vote()
        self.assertEqual(Choice.objects.get(pk=1).votes, 3)
        self.assertEqual(Choice.objects.get(pk=2).votes, 1)

    def test_better_defaults(self):
        poll = Question.objects.create(
            question_text="Are you still there?"
        )
        choice = Choice.objects.create(
            question=poll,
            text_of_choice="I don't blame you."
        )
        self.assertEqual(
            poll.choice_set.all()[0].text_of_choice,
            "I don't blame you."
        )
        self.assertEqual(poll.choice_set.all()[0].votes, 0)

class PollsViewsTestCase(TestCase):
    fixtures = ['view_testdata.json']

    def test_index(self):
        resp = self.client.get(reverse('blog:index'))
        self.assertEqual(resp.status_code, 200)
        self.assertTrue('latest_questions' in resp.context)
        self.assertEqual(
            [poll.pk for poll in resp.context['latest_questions']],
            [1]
        )

        poll_1 = resp.context['latest_questions'][0]
        self.assertEqual(
            poll_1.question_text,
            'Are you learning about testing in Django?'
        )
        self.assertEqual(poll_1.choice_set.count(), 2)

        choices = poll_1.choice_set.all()
        self.assertEqual(choices[0].text_of_choice, 'Yesv')
        self.assertEqual(choices[0].votes, 1)
        self.assertEqual(choices[1].text_of_choice, 'Nov')
        self.assertEqual(choices[1].votes, 0)

    def test_detail(self):
        q1 = Question.objects.get(pk=1)
        resp = self.client.get(reverse('blog:detail', args=(q1.id,)))
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.context['question'].pk, 1)
        self.assertEqual(
            resp.context['question'].question_text,
            'Are you learning about testing in Django?'
        )

        # Ensure that non-existent polls throw a 404.
        q2 = Question.objects.get(pk=2)
        resp = self.client.get(reverse('blog:detail', args=(q2.id,)))
        self.assertEqual(resp.status_code, 404)

    def test_results(self):
        q1 = Question.objects.get(pk=1)
        resp = self.client.get(reverse('blog:results', args=(q1.id,)))
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.context['question'].pk, 1)
        self.assertEqual(
            resp.context['question'].question_text,
            'Are you learning about testing in Django?'
        )

        # Ensure that non-existent polls throw a 404.
        q2 = Question.objects.get(pk=2)
        resp = self.client.get(reverse('blog:results', args=(q2.id,)))
        self.assertEqual(resp.status_code, 404)

    def test_good_vote(self):
        poll_1 = Question.objects.get(pk=1)
        self.assertEqual(poll_1.choice_set.get(pk=1).votes, 1)

        resp = self.client.post(
            reverse('blog:votes', args=(poll_1.id,)),
            {'choice': '1',}
        )
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp['Location'], '/blog/1/results/')
        self.assertEqual(poll_1.choice_set.get(pk=1).votes, 2)

    def test_bad_votes(self):
        # Ensure a non-existant PK throws a Not Found.
        res = self.client.post(reverse('blog:votes', args=(100000,)))
        self.assertEqual(
            res.status_code,
            404
        )

        # Sanity check.
        poll_1 = Question.objects.get(pk=1)
        self.assertEqual(poll_1.choice_set.get(pk=1).votes, 1)

        # Send no POST data.
        resp = self.client.post(reverse('blog:votes', args=(poll_1.id,)))
        self.assertEqual(resp.status_code, 200)

        # Send junk POST data.
        resp = self.client.post(
            reverse('blog:votes', args=(poll_1.id,)),
            {'foo': 'bar'}
        )
        self.assertEqual(resp.status_code, 200)

        # Send a non-existant Choice PK.
        resp = self.client.post(
            reverse('blog:votes', args=(poll_1.id,)),
            {'choice': 300}
        )
        self.assertEqual(resp.status_code, 200)

class QuestionMethodTest(TestCase):
    def test_future_published_date(self):
        future_time = timezone.now() + datetime.timedelta(days=30)
        future_question = Question(pub_date=future_time)
        self.assertEqual(future_question.was_published_recently(), False)
    def test_old_published_date(self):
        old_date = timezone.now() - datetime.timedelta(days=30)
        old_question = Question(pub_date=old_date)
        self.assertEqual(old_question.was_published_recently(), False)

def create_question(text, days):
    return Question.objects.create(
                question_text=text,
                pub_date=timezone.now() + datetime.timedelta(days=days)
            )

class QuestionViewTest(TestCase):

    def test_index_no_quetion(self):
        response = self.client.get(reverse('blog:index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response,"No blogs are available.")
        self.assertQuerysetEqual(response.context['latest_questions'], [])

    def test_index_1_future_question(self):
        future_question = create_question(text="what do you mean", days=2)
        response = self.client.get(reverse('blog:index'))
        self.assertContains(response,"No blogs are available.")
        self.assertQuerysetEqual(response.context['latest_questions'], [])

    def test_index_1_past_question(self):
        past_question = create_question(text="what did you mean", days=-2)
        response = self.client.get(reverse('blog:index'))
        self.assertQuerysetEqual(
            response.context['latest_questions'],
            ['<Question: what did you mean>']
        )

    def test_index_1_future_and_1_past(self):
        past_question = create_question(text="what did you mean", days=-2)
        future_question = create_question(text="what do you mean", days=2)
        response = self.client.get(reverse('blog:index'))
        self.assertQuerysetEqual(
            response.context['latest_questions'],
            ['<Question: what did you mean>']
        )

    def test_index_1_future_and_more_past(self):
        past_1_question = create_question(text="what did you mean", days=-2)
        past_2_question = create_question(text="what did you do", days=-3)
        future_question = create_question(text="what do you mean", days=2)
        response = self.client.get(reverse('blog:index'))
        self.assertQuerysetEqual(
            response.context['latest_questions'],
            ['<Question: what did you mean>', '<Question: what did you do>']
        )

    def test_index_display_max_5_question(self):
        past_1_question = create_question(text="what did you mean 1", days=-2)
        past_2_question = create_question(text="what did you mean 2", days=-3)
        past_3_question = create_question(text="what did you mean 3", days=-4)
        past_4_question = create_question(text="what did you mean 4", days=-5)
        past_5_question = create_question(text="what did you mean 5", days=-6)
        past_6_question = create_question(text="what did you mean 6", days=-7)
        response = self.client.get(reverse('blog:index'))
        self.assertQuerysetEqual(
            response.context['latest_questions'],
            [
                '<Question: what did you mean 1>',
                '<Question: what did you mean 2>',
                '<Question: what did you mean 3>',
                '<Question: what did you mean 4>',
                '<Question: what did you mean 5>'
            ]
        )

class QuestionIndexDetailTests(TestCase):

    def test_detail_view_with_a_future_question(self):
        future_question = create_question(text='Future question.', days=5)
        url = reverse('blog:detail', args=(future_question.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_detail_view_with_a_past_question(self):
        past_question = create_question(text='Past Question.', days=-5)
        url = reverse('blog:detail', args=(past_question.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, past_question.question_text)

    def test_info_question(self):
        question = create_question(text='Question?', days=-2)
        question.choice_set.create(text_of_choice="text1", votes=0)
        question.choice_set.create(text_of_choice="text2", votes=0)
        question.choice_set.create(text_of_choice="text3", votes=1)

        # Perform a vote on the poll by mocking a POST request.
        response = self.client.post('/blog/1/votes/', {'choice': '1',})
        response = self.client.post('/blog/1/votes/', {'choice': '3',})
        url = reverse('blog:results',args=(question.id,))
        response1 = self.client.get(url)

        # In the vote view we redirect the user, so check the
        # response status code is 302.
        self.assertEqual(response.status_code, 302)

        # Get the choice and check there is now one vote.
        choice1 = Choice.objects.get(pk=1)
        choice2 = Choice.objects.get(pk=2)
        choice3 = Choice.objects.get(pk=3)
        self.assertEqual(choice1.votes, 1)
        self.assertEqual(choice2.votes, 0)
        self.assertEqual(choice3.votes, 2)
        self.assertEqual(response1.status_code, 200)
