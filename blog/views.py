from django.http import HttpResponseRedirect
from django.db.models import F
from django.shortcuts import render,get_object_or_404
from django.core.urlresolvers import reverse
from django.views import generic
from django.utils import timezone

from .models import Question, Choice

class IndexView(generic.ListView):
    template_name = 'blog/index.html'
    context_object_name = 'latest_questions'

    def get_queryset(self):
        return Question.objects.filter(pub_date__lte=timezone.now()).order_by('-pub_date')[:5]

class DetailView(generic.DetailView):
    model = Question
    template_name = 'blog/detail.html'

    def get_queryset(self):
        return Question.objects.filter(pub_date__lte=timezone.now())

class ResultsView(generic.DetailView):
    model = Question
    template_name = 'blog/results.html'

    def get_queryset(self):
        return Question.objects.filter(pub_date__lte=timezone.now())

def votes(request, question_id):
    q = get_object_or_404(Question, pk=question_id)

    try:
        selected_choice = q.choice_set.get(pk=request.POST['choice'])
    except (KeyError, Choice.DoesNotExist):
        return render(
                        request,
                        'blog/detail.html',
                        {
                            'question': q,
                            'error_message': "You didnt select any choice!",
                        }
                    )
    else:
        selected_choice.votes = F('votes') + 1
        selected_choice.save()
        return HttpResponseRedirect(reverse('blog:results', args=(q.id,)))

