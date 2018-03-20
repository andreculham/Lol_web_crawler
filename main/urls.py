from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$',views.home),
    url(r'^search/$',views.home),
    url(r'^search/(?P<region>\w+)/$',views.setRegion),
    url(r'^search/(?P<region>\w+)/(?P<search_value>[\w ]+)/$',views.search),
    url(r'^update/(?P<region>\w+)/(?P<search_value>[\w ]+)/$',views.update),
    url(r'^workload/$', views.workload, name='workload'),
    url(r'^api_caller/$', views.index),
    url(r'^champions/(?P<region>\w+)/$', views.champions),
    url(r'^champions/(?P<region>\w+)/(?P<league>\w+)/(?P<time>\w+)/$',views.champions),
]
