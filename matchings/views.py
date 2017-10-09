from django.shortcuts import render
from django.views.generic import ListView
from django.views.generic.base import TemplateView
from django.views.generic.edit import FormView

from django.db.models import Q

from matchings.models import Disease, Prescription_List
from matchings.forms import PrescriptionSearchForm

# Create your views here.

class datashow(ListView):
	template_name = 'datashow.html'

	def get_queryset(self):
		return Disease.objects.order_by('-STARTDATE')[:10]

class PrescriptionSearchFormView(FormView):
	form_class = PrescriptionSearchForm
	template_name = 'disease_search.html'

	def form_valid(self, form):
		schWord = '%s' % self.request.POST['search_word']
		prescription_list = Prescription_List.objects.filter(Q(ORDERCODE__icontains=schWord)).distinct()

		context = {}
		context['form'] = form
		context['search_term'] = schWord
		context['object_list'] = prescription_list

		return render(self.request, self.template_name, context)




class m4876_00(TemplateView):
	template_name = 'm4876.html'

class m4876_01(TemplateView):
	template_name = 'm4876_01.html'
