from django.conf.urls import url
from matchings import views

urlpatterns = [
	url(r'^$', views.datashow.as_view(), name='datashow'),
	url(r'^match_disease/$', views.MatchFormView.as_view(), name='match_disease'),
	url(r'^model_comparison/', views.MatchFormView, name='models_test'),
	url(r'^m4876_00/$', views.m4876_00.as_view(), name='m4876_00'),
	url(r'^m4876_01/$', views.m4876_01.as_view(), name='m4876_01'),
]
