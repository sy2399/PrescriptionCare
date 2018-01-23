from django.conf.urls import url
from matchings import views

urlpatterns = [
	url(r'^$', views.datashow.as_view(), name='datashow'),
	
	url(r'^match_disease/$', views.match_disease, name='match_disease'),
	url(r'^match_disease/search_prescription/$', views.search_prescription, name='search_prescription'),
	url(r'^match_disease/search_disease/$', views.search_disease, name='search_disease'),

	url(r'^static/$', views.statics, name='statics'),
	
	url(r'^model_comparison/', views.ModelCompareFormView.as_view(), name='models_test'),
	url(r'^userstatics/$', views.UserStatics.as_view(), name='userstatics'),
	url(r'^usermanagement/$', views.UserManagement.as_view(), name='usermanagement'),
	url(r'^userservice_search/$', views.userservice_search, name='userservice_search'),
	url(r'^userservice/$', views.userservice, name='userservice'),
	url(r'^updatemodel/$', views.updatemodel, name='updatemodel'),

	url(r'^network/$', views.network, name='network'),
	url(r'^m4876_00/$', views.m4876_00.as_view(), name='m4876_00'),
	url(r'^m4876_01/$', views.m4876_01.as_view(), name='m4876_01'),
]
