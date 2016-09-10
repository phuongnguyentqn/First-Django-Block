import datetime
from django.test import TestCase
from django.utils import timezone
from django.core.urlresolvers import reverse

from .models import Question, Choice
# Create your tests here.
class QuestionMethodTest(TestCase):
    def test_future_published_date(self):
        future_time = timezone.now() + datetime.timedelta(days=30)
        future_question = Question(pub_date=future_time)
        self.assertEqual(future_question.was_published_recently(), False)
    def test_old_published_date(self):
        old_date = timezone.now() - datetime.timedelta(days=30)
        old_question = Question(pub_date=old_date)
        self.assertEqual(old_question.was_published_recently(), False)
    def test_recent_published_date(self):
        recent_time = timezone.now() - datetime.timedelta(hours=1)
        recent_question = Question(pub_date = recent_time)
        self.assertEqual(recent_question.was_published_recently(), True)

def create_question(text, days):
    return Question.objects.create(question_text = text, pub_date = timezone.now() + datetime.timedelta(days=days))

class QuestionViewTest(TestCase):
    def test_index_no_quetion(self):
        response = self.client.get(reverse('blog:index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response,"No blogs are available.")
        self.assertQuerysetEqual(response.context['latest_questions'], [])
    def test_index_1_future_question(self):
        future_question = create_question(text = "what do you mean", days = 2)
        response = self.client.get(reverse('blog:index'))
        self.assertContains(response,"No blogs are available.")
        self.assertQuerysetEqual(response.context['latest_questions'], [])
    def test_index_1_past_question(self):
        past_question = create_question(text = "what did you mean", days = -2)
        response = self.client.get(reverse('blog:index'))
        self.assertQuerysetEqual(response.context['latest_questions'], ['<Question: what did you mean>'])

    def test_index_1_future_and_1_past(self):
        past_question = create_question(text = "what did you mean", days = -2)
        future_question = create_question(text = "what do you mean", days = 2)
        response = self.client.get(reverse('blog:index'))
        self.assertQuerysetEqual(response.context['latest_questions'],['<Question: what did you mean>'])
        
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
        self.assertContains(response, past_question.question_text)


