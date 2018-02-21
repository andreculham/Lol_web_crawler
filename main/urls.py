from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^workload/$', views.workload, name='workload'),
    url(r'^search/$' , views.home, name = 'home'),
    url(r'^search/(?P<search_value>[\w]+)/$', views.search , name = 'search'),
]
