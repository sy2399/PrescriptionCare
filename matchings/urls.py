from django.conf.urls import url
from matchings import views
from matchings.forms import DiseaseSearchForm

urlpatterns = [
	url(r'^$', views.datashow.as_view(), name='datashow'),
	url(r'^disease_search/$', views.SearchFormView.as_view(), name='disease_search'),
	url(r'^m4876_00/$', views.m4876_00.as_view(), name='m4876_00'),
	url(r'^m4876_01/$', views.m4876_01.as_view(), name='m4876_01'),
]
