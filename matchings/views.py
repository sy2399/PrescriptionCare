from django.template.context_processors import csrf

from django.shortcuts import render_to_response, render
from django.http import HttpResponseRedirect
from django.http import HttpResponse

from django.shortcuts import render
from django.views.generic import ListView
from django.views.generic.base import TemplateView
from django.views.generic.edit import FormView

from django.db.models import Q

from matchings.models import Disease, Prescription_List
from matchings.forms import MatchForm

from matchings.neural_net_model import NeuralNetwork
from matchings.graph_model import NetworkxModel

import pandas as pd
import pickle

class datashow(ListView):
	template_name = 'datashow.html'

	def get_queryset(self):
		return Disease.objects.order_by('-STARTDATE')[:10]

class MatchFormView(FormView):
	form_class = MatchForm
	template_name = 'disease_search.html'

	def form_valid(self, form):
		schWord = '%s' % self.request.POST['match_word']
		#prescription_list = Prescription_List.objects.filter(Q(ORDERCODE__icontains=schWord)).distinct()

		model = NetworkxModel()
		context = {}
		context['form'] = form
		context['search_term'] = schWord
		context['disease_list'] = model.get_disease_by_networkx(dxcode_input=schWord)

		return render(self.request, self.template_name, context)

def match_disease(request):
	args = {}
	args.update(csrf(request))
	args['prescription_list'] = Prescription_List.objects.all()

	return render_to_response('disease_search.html', args)

def search_prescription(request):
	if request.method == "POST":
		search_text = request.POST['search_text']
	else:
		search_text = ''

	prescriptions = Prescription_List.objects.filter(ORDERCODE__contains=search_text)	

	return render_to_response('ajax/ajax_prescription_search.html', {'prescriptions': prescriptions})

def save_prescription(request):
	if request.method == "POST":
		save_text = request.POST['save_text']


class ModelCompareFormView(FormView):
	form_class = MatchForm
	template_name = 'models_test_page.html'
	
#	pickle.dump(self.vect, open("vectorizer.pickle", "wb"))
#
#	with open("vectorizer.pickle", "rb") as f:
#			vectorizer = pickle.load(f)
#
#	json_file = open("static/NN_model.json", "r")
#	loaded_N_model_json = json_file.read()
#	json_file.close()
#
#	loaded_model = model_from_json(loaded_N_model_json)
#
#	loaded_model.load_weights("NN_model.h5")
#	#print("Loaded model from disf")
#	loaded_model.compile(loss='binary_crossentropy', optimizer='rmsprop', metrics=['accuracy'])


	NNmodel = NeuralNetwork()	
#	NXmodel = NetworkxModel()
	
	def form_valid(self, form):
		schWord = '%s' % self.request.POST['match_word']
		#prescription_list = Prescription_List.objects.filter(Q(ORDERCODE__icontains=schWord)).distinct()

		context = {}
		context['form'] = form
		context['search_term'] = schWord
		context['neuralnet_disease_list'] = self.NNmodel.get_disease(dxcode_input=schWord)
#		context['networkx_disease_list'] = self.NXmodel.get_disease(dxcode_input=schWord)

		return render(self.request, self.template_name, context)


class m4876_00(TemplateView):
	template_name = 'm4876.html'

class m4876_01(TemplateView):
	template_name = 'm4876_01.html'
