from django.template.context_processors import csrf

from django.shortcuts import render_to_response, render
from django.http import HttpResponseRedirect
from django.http import HttpResponse

from django.shortcuts import render
from django.views.generic import ListView
from django.views.generic.base import TemplateView
from django.views.generic.edit import FormView
from django.template import RequestContext

from django.db.models import Q

from django.contrib.auth.models import User
from matchings.models import Disease, Disease_name, Prescription
from matchings.forms import MatchForm

#from matchings.neural_net_model import NeuralNetwork
from matchings.networkx_model import NetworkX

import pandas as pd
import numpy as np
import pickle


#diseasedf = pd.DataFrame(list(Disease.objects.all().values('dxcode', 'prescriptionlist')))
prescriptiondf = pd.DataFrame(list(Prescription.objects.all().values('ordercode', 'ordername')))
#namedf['dxcode'] = namedf['icdcode']
#del namedf['icdcode']
#df = pd.merge(df, namedf, on='dxcode')

# drop rows which contain nan
#df = df.dropna(how="any")

#NNmodel = NeuralNetwork()
NXmodel = NetworkX()

class datashow(ListView):
	template_name = 'datashow.html'

	def get_queryset(self):
		return Disease.objects.all()[0:10]


def match_disease(request):
	context = {}
	context.update(csrf(request))
	context['prescriptions'] = Prescription.objects.all()
	context['user'] = request.user


	if request.method == "POST":
#		print("##############################")

#		inputPreCode = request.POST.get('inputPreCode', '')
#		inputPreCodeName = request.Post.get('inputPreCodeName', '')
#		checked_discode = request.Post.get('checked_discode', '')
#		checked_disname = request.Post.get('checked_disname', '')
#		notice = request.Post.get('noticeArea', '')
#		flag = request.Post.get('flag', '')
#
#		print(inputPreCode)
#		print('///')
#		print(inputPreCodeName)
#		print('///')
#		print(checked_discode)
#		print('///')
#		print(checked_disname)
#		print('///')
#		print(notice)
#		print('///')
#		print(flag)
#
#		print("##############################")
#

		print(request.POST)

	return render(request, 'disease_search.html', context)

def search_prescription(request):
	if request.method == "POST":
		search_text = request.POST['search_text']

		print(request.POST)
	else:
		search_text = ''

	prescriptions = Prescription.objects.filter(Q(ordercode__icontains=search_text) | Q(ordername__icontains=search_text))

	context = {}
	context['prescriptions'] = prescriptions

	return render(request, 'ajax/ajax_prescription_search.html', context)

def search_disease(request):
	if request.method == "POST":
		search_list = request.POST['search_list']
	else:
		search_list = ''
	
	context = {}
	context['search_term'] = search_list
	#idx = prescriptiondf["ordercode"][prescriptiondf["ordercode"].split(" ")[0]==search_list].index()


	# context['search_term'] = Prescription.objects.get()

#for seperating main/sub disease
#	context['main_NN_disease_list'] = NNmodel.get_disease(dxcode_input=search_list, num=5)
#	context['sub_NN_disease_list'] = sub_NNmodel.get_disease(dxcode_input=search_list, num=10)
#	context['main_NX_disease_list'] = main_NXmodel.get_disease(dxcode_input=search_list, num=5)
#	context['sub_NX_disease_list'] = sub_NXmodel.get_disease(dxcode_input=search_list, num=10)

# for non seperating main/sub disease
#	context['NN_disease_list'] = NNmodel.get_disease(dxcode_input=search_list, num=10)

	disease_list = NXmodel.get_disease(dxcode_input=search_list, num=10)
	context['NX_disease_list'] = disease_list

#	disease_name_list = []
#
#	connection = {}
#
#	for i in np.arange(len(disease_list)):
#		connection[i] = NXmodel.find_dxcode(disease_list[i][0])[:10]
#	
#	context['connection'] = connection

#	print(search_list)
#	print(context['disease_list'])
#	context['neuralnet_disease_list'] = self.NNmodel.get_disease(dxcode_input=schWord)
#		context['networkx_disease_list'] = self.NXmodel.get_disease(dxcode_input=schWord)

	return render(request, 'ajax/ajax_disease_search.html', context)

class ModelCompareFormView(FormView):
	form_class = MatchForm
	template_name = 'models_test_page.html'
	
#	NNmodel = NeuralNetwork()	
#	NXmodel = NetworkxModel()
	
	def form_valid(self, form):
		schWord = '%s' % self.request.POST['match_word']
		#prescription_list = Prescription_List.objects.filter(Q(ORDERCODE__icontains=schWord)).distinct()

		context = {}
		context['form'] = form
		context['search_term'] = schWord
		context['neuralnet_disease_list'] = NNmodel.get_disease(dxcode_input=schWord)
#		context['networkx_disease_list'] = self.NXmodel.get_disease(dxcode_input=schWord)

		return render(self.request, self.template_name, context)

class UserStatics(ListView):
	template_name = 'userstatics.html'

	def get_queryset(self):
		return User.objects.filter(is_superuser=False)

class UserManagement(ListView):
	template_name = 'usermanagement.html'

	def get_queryset(self):
		return User.objects.filter(is_superuser=False)

class UserService(ListView):
	template_name = "userservice.html"

	def get_queryset(self):
		return User.objects.filter(is_superuser=False)

class m4876_00(TemplateView):
	template_name = 'm4876.html'

class m4876_01(TemplateView):
	template_name = 'm4876_01.html'
