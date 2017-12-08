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
from matchings.models import Disease, Disease_name, Prescription, Review, Notice, Doctor_diagnose 
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
		print(request.POST)

		inputPreCode = request.POST.get("inputPreCode").split(" ")[1]
		print(inputPreCode)
		inputPreName = Prescription.objects.get(Q(ordercode=inputPreCode)).ordername
		noticeArea = request.POST.get("noticeArea")
		if request.POST.get("flag") == "option1":
			flag = False
		else:
			flag = True
		
		if Notice.objects.filter(Q(ordercode=inputPreCode)).count() == 1:
			notice = Notice.objects.get(Q(ordercode=inputPreCode))
			notice.notice_description = noticeArea
			notice.display_condition = flag
			notice.save()
		else:
			notice = Notice(
						ordercode=inputPreCode,
						ordername=inputPreName,
						notice_description=noticeArea,
						display_condition=flag
					)
			notice.save()


		for checked_dxcode in request.POST.getlist("checked_discode"):
			if Review.objects.filter(Q(ordercode=inputPreCode) & Q(dxcode=checked_dxcode)).count() == 1:
				review = Review.objects.get(Q(ordercode=inputPreCode) & Q(dxcode=checked_dxcode))
				review.frequency += 1
				review.save()
			else:
				review = Review(
							ordercode=inputPreCode,
							dxcode=checked_dxcode,
							#dxcode_name
						)
				review.save()


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

	disease_list = NXmodel.get_disease(ordercode_input=search_list, num=10)
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
#	context['neuralnet_disease_list'] = self.NNmodel.get_disease(ordercode_input=schWord)
#		context['networkx_disease_list'] = self.NXmodel.get_disease(ordercode_input=schWord)

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
		context['neuralnet_disease_list'] = NNmodel.get_disease(ordercode_input=schWord)
#		context['networkx_disease_list'] = self.NXmodel.get_disease(ordercode_input=schWord)

		return render(self.request, self.template_name, context)

class UserStatics(ListView):
	template_name = 'userstatics.html'

	def get_queryset(self):
		return User.objects.filter(is_superuser=False)

class UserManagement(ListView):
	template_name = 'usermanagement.html'

	def get_queryset(self):
		return User.objects.filter(is_superuser=False)

class UserService(FormView):
	form_class = MatchForm
	template_name = 'userservice.html'

	def form_valid(self, form):
		schWord = '%s' % self.request.POST['match_word']

		print(schWord)

		search_prescription_list = []
		for code in schWord.split(" "):
			if Notice.objects.filter(ordercode=code).count() != 1:
				continue
			search_prescription = Notice.objects.get(ordercode=code)

			search_prescription_list.append(search_prescription)

		hosp_prescriptions = []
		for code in schWord.split(" "):
			#print(Review.objects.filter(ordercode=code).count())
			if Review.objects.filter(ordercode=code).count() == 0:
				continue
		
			hosp_prescription = Review.objects.filter(ordercode=code)
			for item in hosp_prescription:
				hosp_prescriptions.append(item)

		sys_prescriptions = []
		networkx_disease_lists = []
		for code in schWord.split(" "):
			if Prescription.objects.filter(ordercode=code).count() != 1:
				continue
			sys_prescription = Prescription.objects.get(ordercode=code)
			
			if Notice.objects.filter(ordercode=code).count() == 1:
				notice = Notice.objects.get(ordercode=code)

				if notice.display_condition == False:
					continue

			elif Notice.objects.filter(ordercode=code).count() == 0:
				notices.append("No message recorded")
			else:
				print("More than 2 notice objects has the same ordercode!!!!!!!!!!!!!!!!!!")
				continue

			sys_prescriptions.append(sys_prescription)
		

			networkx_disease_list = NXmodel.get_disease(ordercode_input=schWord, num=3)
			networkx_disease_lists.append(networkx_disease_list)

		context = {}
		context["hosp_prescriptions"] = hosp_prescriptions

		context["sys_prescriptions"] = zip(sys_prescriptions, networkx_disease_list)
		#context['networkx_disease_lists'] = networkx_disease_lists
		
		#context["prescription_list"] = zip(hosp_prescriptions, notices)
		context["search_prescription_list"] = search_prescription_list
		

		return render(self.request, self.template_name, context)


class m4876_00(TemplateView):
	template_name = 'm4876.html'

class m4876_01(TemplateView):
	template_name = 'm4876_01.html'
