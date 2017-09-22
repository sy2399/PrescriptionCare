from django.shortcuts import render
from django.views.generic import ListView
from django.views.generic.base import TemplateView

from matchings.models import Disease, Prescription
# Create your views here.

class datashow(ListView):
	template_name = 'datashow.html'

	def get_queryset(self):
		return Disease.objects.order_by('-STARTDATE')[:10]

class m4876_00(TemplateView):
	template_name = 'm4876.html'

class m4876_01(TemplateView):
	template_name = 'm4876_01.html'
