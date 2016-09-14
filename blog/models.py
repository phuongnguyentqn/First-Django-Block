import datetime
from django.db import models

class Question(models.Model):
    question_text =  models.CharField(max_length=200)
    pub_date = models.DateTimeField(
        'published date',
        default=datetime.datetime.now
    )

    def __str__(self):
        return self.question_text

    def was_published_recently(self):
        return self.pub_date.date() == datetime.date.today()
    was_published_recently.admin_order_field = 'pub_date'
    was_published_recently.boolean = True
    was_published_recently.short_description = 'Published recently?'

class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    text_of_choice = models.CharField(max_length=200)
    votes = models.IntegerField(default=0)

    def __str__(self):
        return self.text_of_choice

    def record_vote(self):
        self.votes += 1
        self.save()
