from django.conf.urls import url
from . import views
from django.contrib import admin

app_name = 'blog'

urlpatterns = [
	#ex: /blog/
	url(r'^admin/$', admin.site.urls),
    url(r'^$', views.IndexView.as_view() , name='index'),
    #ex: /blog/5/
    url(r'^(?P<pk>\d+)/$', views.DetailView.as_view(), name='detail'),
    #ex: /blog/5/results/
    url(
        r'^(?P<pk>\d+)/results/$', views.ResultsView.as_view(), name='results'),
    #ex: /blog/5/vote/
    url(r'^(?P<question_id>\d+)/votes/$', views.votes, name='votes'),
]
