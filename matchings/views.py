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

		# inputPreCode = request.POST.get("inputPreCode").split(" ")[1]
		inputPreCode = request.POST.get("inputPreCode")  # .split(" ")[1]

		inputPreCode = request.POST.get("inputPreCode")#.split(" ")[1]
		print(inputPreCode)
		inputPreName = Prescription.objects.get(Q(ordercode=inputPreCode)).ordername
		noticeArea = request.POST.get("noticeArea").strip()
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

		##########################################
		# 수정 by khan
		##########################################
		# 해당 처방에 대한 기존 상병은 모두 삭제함
		Review.objects.filter(Q(ordercode=inputPreCode)).delete()
		# 새롭게 업데이트된 선택 결과를 삽입
		for checked_dxcode in request.POST.getlist("checked_discode"):
			review = Review(
				ordercode=inputPreCode,
				dxcode=checked_dxcode,
				# dxcode_name
			)
			review.save()
			'''
			if Review.objects.filter(Q(ordercode=inputPreCode) & Q(dxcode=checked_dxcode)).count() == 1: # 존재하는 경우
				#review = Review.objects.get(Q(ordercode=inputPreCode) & Q(dxcode=checked_dxcode))
				#review.frequency += 1
				#review.save()
			else: # 없는 경우 새로 기록
			'''


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
		search_list = request.POST['search_list'].strip()
	else:
		search_list = ''

	context = {}
	context['search_term'] = search_list
	#idx = prescriptiondf["ordercode"][prescriptiondf["ordercode"].split(" ")[0]==search_list].index()


	# context['search_term'] = Prescription.objects.get()


	######################################################
	#  Added by khan Dec. 14 2017
	######################################################
	print("search_list: ", search_list)
	disease_list = NXmodel.get_disease(ordercode_input=search_list, num=10)
	context['NX_disease_list'] = disease_list

	#해당 처방에 대한 Review 정보 받아오기
	selected_list = []
	#if Review.objects.filter(Q(ordercode=search_list)).count() != 0:
	reviews = Review.objects.filter(Q(ordercode=search_list))
	print(reviews)

	#이미 선택된 상병인지 확인을 위한 코드
	for disease in disease_list: # disease list is always filled with onl 1 item
		selected = 0
		for review in reviews:
			if disease[0] == review.dxcode:
				selected = 1
				break
		if selected == 1:
			selected_list.append([disease, 1])
		else:
			selected_list.append([disease, 0])
		
	#else:
	#	print("해당 처방 리뷰 정보 없음")

	context['NX_disease_list'] = selected_list

	#해당 처방에 대한 Notice 정보 받아오기
	#if Notice.objects.filter(Q(ordercode=search_list)).count() == 1:#정보가 있으면 (단일만 가능# )
		
	# 해당 처방에 대한 Review 정보 받아오기
	selected_list = []
	#if Review.objects.filter(Q(ordercode=search_list)).count() != 0: # 정보가 있으면 (복수 가능)
	reviews = Review.objects.filter(Q(ordercode=search_list))
	print(reviews)

	# 이미 선택된 상병인지 확인을 위한 코드
	for disease in disease_list:
		selected = 0
		for review in reviews:
			if disease[0] == review.dxcode:
				selected = 1
				break
		if selected == 1:
			selected_list.append([disease, 1])
		else:
			selected_list.append([disease, 0])
#	else:
#		print("해당처방 리뷰 정보 없음")

	context['NX_disease_list'] = selected_list
	
	######################################################
	# 해당 처방에 대한 Notice 정보 받아오기
	if Notice.objects.filter(Q(ordercode=search_list)).count() == 1: # 정보가 있으면 (단일만 가능)
		notice = Notice.objects.get(Q(ordercode=search_list))
		print(notice.notice_description)
		context['notice'] = notice
	else:
		print("해당 처방 Notice 정보 없음")
		context['notice'] = ''

	######################################################
	# End by khan
	######################################################


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


def userservice(request):
	if request.method == 'POST':
		if request.POST.get('match_word') is not None:
			schWord = '%s' % request.POST['match_word']
		else:
			schWord = ''

			print(request.POST)			


	else:
		schWord = ''

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
		#	notice.append("No message recorded")
			print("No dxcode " + code + " in notice!!")
		else:
			print("More than 2 notice objects has the same ordercode!!!!!!!!!!!!!!!!!!")
			continue

		sys_prescriptions.append(sys_prescription)


		networkx_disease_list = NXmodel.get_disease(ordercode_input=schWord, num=3)
		networkx_disease_lists.append(networkx_disease_list)

	context = {}
	context['schword'] = schWord
	context["hosp_prescriptions"] = hosp_prescriptions

	context["sys_prescriptions"] = zip(sys_prescriptions, networkx_disease_lists)
	#context['networkx_disease_lists'] = networkx_disease_lists

	#context["prescription_list"] = zip(hosp_prescriptions, notices)

	context["search_prescription_list"] = zip(np.arange(1, 1 + len(search_prescription_list)).tolist(), search_prescription_list)


	return render(request, 'userservice.html', context)

def check_diagnose(request):
	#if request.method == 'POST':
		

	return render(request, 'userservice.html')




class m4876_00(TemplateView):
	template_name = 'm4876.html'

class m4876_01(TemplateView):
	template_name = 'm4876_01.html'
