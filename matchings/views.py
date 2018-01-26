from django.template.context_processors import csrf

from django.shortcuts import render_to_response, render, redirect
from django.http import HttpResponseRedirect
from django.http import HttpResponse

from django.shortcuts import render
from django.views.generic import ListView
from django.views.generic.base import TemplateView
from django.views.generic.edit import FormView
from django.template import RequestContext

from django.db.models import Q
from django.contrib.auth.decorators import user_passes_test, login_required
from django.utils.decorators import method_decorator

from django.contrib.auth.models import User
from matchings.models import Disease, Disease_name, Prescription, Review, Notice, Doctor_diagnose, UploadFileModel, RemodelTime
from matchings.forms import MatchForm

from matchings.neural_net_model import NeuralNetwork
from matchings.forms import UploadFileForm
from matchings.networkx_model import NetworkX

from userprofile.models import UserProfile

import pandas as pd
import numpy as np
import threading
import pickle
import json
from datetime import date
from datetime import datetime
from collections import OrderedDict, Counter


#	Dataframes	#
diseasedf = pd.DataFrame(list(Disease.objects.all().values('dxcode', 'prescriptionlist', 'frequency', 'fileflag')))
prescriptiondf = pd.DataFrame(list(Prescription.objects.all().values('ordercode', 'ordername')))
# drop rows which contain nan
prescriptiondf = prescriptiondf.dropna(how="any")
diseasenamedf = pd.DataFrame(list(Disease_name.objects.all().values('icdcode', 'namek') ))

NNmodel = NeuralNetwork()
NXmodel = NetworkX()

time = RemodelTime.objects.latest('endtime')
time.status = False
time.save()

@method_decorator(login_required, name='dispatch')
class datashow(ListView):
	template_name = 'datashow.html'

	def get_queryset(self):
		return Disease.objects.all()[0:10]

@login_required
def match_disease(request):
	context = {}
	context.update(csrf(request))
	context['prescriptions'] = Prescription.objects.all()
	context['user'] = request.user

	if request.method == "POST":
		print(request.POST)

		inputPreCode = request.POST.get("inputPreCode")
		print(inputPreCode)
		inputPreName = Prescription.objects.get(Q(ordercode=inputPreCode)).ordername
		noticeArea = request.POST.get("noticeArea").strip()
		print("flag: ", request.POST.get("flag"))
		if request.POST.get("flag") == "option1":
			flag = False
		else:
			flag = True
		print("flag: ", flag)

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
			if (Review.objects.filter(Q(ordercode=inputPreCode) & Q(dxcode=checked_dxcode)).count()) == 0:
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

#상병 검색시
@login_required
def search_prescription(request):
	if request.method == "POST":
		search_text = request.POST['search_text']

		print(request.POST)
	else:
		search_text = ''

	#상병의 이름 혹은 코드 중 seach_text가 포함된 상병들을 찾아냄	
	prescriptions = Prescription.objects.filter(Q(ordercode__icontains=search_text) | Q(ordername__icontains=search_text))

	context = {}
	context['prescriptions'] = prescriptions
	context['prescriptions_cnt'] = len(prescriptions)

	return render(request, 'ajax/ajax_prescription_search.html', context)

#처방을 클릭해서 상병을 검색할 경우
@login_required
def search_disease(request):
	if request.method == "POST":
		search_list = request.POST['search_list'].strip()
	else:
		search_list = ''

	context = {}
	context['search_term'] = search_list

	######################################################
	#  Added by khan Dec. 14 2017
	######################################################
	#print("search_list: ", search_list)
	NN_disease_list = NNmodel.get_disease(ordercode_input=search_list, num=15)
	NX_disease_list = NXmodel.get_disease(ordercode_input=search_list, num=15)

	print("NN: ", NN_disease_list)
	print("")
	print("NX: ", NX_disease_list)
	print("")
	#####################################################
	#	Code for comparing results of NN, NX			#
	#####################################################

	disease_list = []
	for item in NX_disease_list[0:6]:
		disease_list.append(item)

	print(disease_list)

	for item in NN_disease_list:
		exist_flag = False
		for code in NX_disease_list[0:6]:
			#print("item: ", item[0], "code: ", code[0])
			if item[0] == code[0]:
				exist_flag = True
				break
		
		if (exist_flag == False) and (len(disease_list) < 15):
			disease_list.append(item)

#for item in NN_disease_list[5:10]:
#		if len(disease_list) < 10:
#			disease_list.append(item)
#		else:
#			break
	print("disease_list: ", disease_list)

	#해당 처방에 대한 Review 정보 받아오기
	reviews = Review.objects.filter(Q(ordercode=search_list))
	selected_list = []
	#print(reviews)

	#이미 선택된 상병인지 확인을 위한 코드
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
		
	print("sel_list: ", selected_list)

	context['disease_list'] = selected_list
	context['disease_list_cnt'] = len(selected_list)

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

	return render(request, 'ajax/ajax_disease_search.html', context)


######################################################
#	Code for webpage that compares NN and NX model   #
######################################################
@method_decorator(login_required, name='dispatch')
class ModelCompareFormView(FormView):
	form_class = MatchForm
	template_name = 'models_test_page.html'

	def form_valid(self, form):
		schWord = '%s' % self.request.POST['match_word']

		context = {}
		context['form'] = form
		context['search_term'] = schWord
		context['neuralnet_disease_list'] = NNmodel.get_disease(ordercode_input=schWord)

		return render(self.request, self.template_name, context)

@login_required
def statics(request):
	context = {}

	df = diseasedf[['dxcode', 'frequency', 'fileflag']]	
	df = df[df.fileflag==True]
	df = df.drop_duplicates(subset='dxcode').sort_values('frequency', ascending=False)[0:25]
	data = []
	for _, item in df.iterrows():
		dic = {}
		dic["dxcode"] = item['dxcode']
		dic["frequency"] = item['frequency']
		data.append(dic)

	diagnoses_data = []
	network_data = []

	if request.method == "POST":
		search_dxcode = request.POST['search_dxcode']
		print("request: ", search_dxcode)

		diagnoses = Doctor_diagnose.objects.filter(Q(dxcode=search_dxcode))

		for item in diagnoses:
			dic = {}
			dic["ordercode"] = item.ordercode
			dic["frequency"] = item.frequency

			diagnoses_data.append(dic)

		dis = Disease.objects.filter(Q(dxcode=search_dxcode) & Q(fileflag=True))

		network_data = OrderedDict()
		network_data["nodes"] = []
		network_data["links"] = []

		ordernodelist = []
		ordernodecountlist = []
		for item in dis:
			for ordercode in item.prescriptionlist.split(' '):				
				ordernodecountlist.append(ordercode)
				if ordercode in ordernodelist:
					continue
				ordernodelist.append(ordercode)
				node_dic = {}
				node_dic["id"] = ordercode
				node_dic["group"] = 2
				
				link_dic = {}
				link_dic["source"] = search_dxcode
				link_dic["target"] = ordercode
				
				network_data["nodes"].append(node_dic)
				network_data["links"].append(link_dic)

		weight = dict(Counter(ordernodecountlist).most_common(30))
				
		for item in network_data["nodes"]:
			if item["id"] in weight.keys():
				item["weight"] = weight[item["id"]]
			if Prescription.objects.filter(Q(ordercode=item["id"])).count() == 1:
				ordername = Prescription.objects.get(Q(ordercode=item["id"])).ordername
				item["name"] = ordername
			else:
				item["name"] = "Unknown"

		for item in network_data["links"]:
			if item["target"] in weight.keys():
				item["weight"] = weight[item["target"]]

		network_data["nodes"] = [d for d in network_data["nodes"] if d.get("weight")]
		
		if Disease_name.objects.filter(Q(icdcode=search_dxcode)).count() == 1:
			disname = Disease_name.objects.get(Q(icdcode=search_dxcode)).namek
		else:
			disname = "Unknown" + "(" + search_dxcode + ")"

		network_data["nodes"].append({"id": search_dxcode, "group": 1, "weight": sum(weight.values()), "name": disname})
		network_data["links"] = [d for d in network_data["links"] if d.get("weight")]

	context['tsvdata'] = json.dumps(data)
	context['network_data'] = json.dumps(network_data)
	context['diagnoses_data'] = json.dumps(diagnoses_data)

	return render(request, 'statics.html', context)

@method_decorator(login_required, name='dispatch')
class UserStatics(ListView):
	template_name = 'userstatics.html'

	def get_queryset(self):
		return User.objects.filter(is_superuser=False)

@method_decorator(user_passes_test(lambda u: u.is_superuser), name='dispatch')
class UserManagement(ListView):
	template_name = 'usermanagement.html'

	def get_queryset(self):
		return User.objects.filter(is_superuser=False)
	
	def post(self, request):
		print("post: ", request.POST)
		name = request.POST.get('user_name')
		sday = request.POST.get('sday')
		eday = request.POST.get('eday')

		if sday is '' or eday is '':
			#profile = UserProfile.objects.filter(Q(assigned_group=name))
			filtered_user = User.objects.filter(
				Q(is_superuser=False) & 
				(Q(first_name=name) | Q(userprofile__customer=name))
			)
			print(filtered_user)
		else:
			print(UserProfile.objects.filter(Q(contract_end_date=eday)))
			if name is '':
				filtered_user = User.objects.filter(
					Q(is_superuser=False) & 
					Q(userprofile__contract_start_date__gte=sday) &
					Q(userprofile__contract_end_date__lte=eday)
				)
			else:
				filtered_user = User.objects.filter(
					Q(is_superuser=False) & 
					(Q(first_name=name) | Q(userprofile__customer=name)) &
					Q(userprofile__contract_start_date__lte=sday) &
					Q(userprofile__contract_end_date__gte=eday)

				)

		context = {}
		context['user_list'] = filtered_user
		
		return render(request, self.template_name, context)

@login_required
def userservice_search(request):
	return render(request, 'userservice_search.html')

@login_required
def userservice(request):
	if request.method == 'POST':
		if request.POST.get('match_word') is not None:
			schWord = '%s' % request.POST['match_word']
		else:
			schWord = ''

			print(request.POST)
			for ordercode, dxcode in zip(request.POST.getlist('checked_precode'), request.POST.getlist('checked_discode')):
				if Doctor_diagnose.objects.filter(Q(ordercode=ordercode) & Q(dxcode=dxcode)).count() != 0:
					diag = Doctor_diagnose.objects.get(Q(ordercode=ordercode) & Q(dxcode=dxcode))
					diag.frequency = str(int(diag.frequency) + 1) # this should be fixed
					diag.save()
				else:
					diag = Doctor_diagnose(
								ordercode = ordercode,
								dxcode = dxcode,
								frequency = 1
							)
					diag.save()
			
				if Disease.objects.filter(Q(dxcode=dxcode) & Q(prescriptionlist=ordercode) & Q(fileflag=False)).count() != 0:
					dis = Disease.objects.get(Q(prescriptionlist=ordercode) & Q(dxcode=dxcode) & Q(fileflag=False))
					dis.frequency = str(int(dis.frequency) + 1) # this should be fixed
					dis.save()
				else:
					dis = Disease(
								dxcode = dxcode,
								prescriptionlist = ordercode,
								frequency = 1,
								fileflag = False
							)
					dis.save()
			
			return redirect('/matchings/userservice_search/')

	else:
		schWord = ''


	print("Search word: ", schWord)

	search_prescription_list = []
	for code in schWord.split(" "):
		if Notice.objects.filter(ordercode=code).count() != 1:
			continue
		search_prescription = Notice.objects.get(ordercode=code)
		search_prescription_list.append(search_prescription)

	hosp_prescriptions = []
	hosp_disease_name_list = []
	hosp_prescriptions_fre = []
	for code in schWord.split(" "):
		if Review.objects.filter(ordercode=code).count() == 0:
			continue

		hosp_prescription = Review.objects.filter(ordercode=code)
		for item in hosp_prescription:
			hosp_prescriptions.append(item)
	
			if (diseasenamedf['icdcode'] != item.dxcode).all():
				hosp_disease_name_list.append("Unknown")
			else:
				idx = diseasenamedf['icdcode'][diseasenamedf['icdcode'] == item.dxcode].index[0]
				hosp_disease_name_list.append(diseasenamedf['namek'][idx])
	
			if Doctor_diagnose.objects.filter(Q(ordercode=item.ordercode) & Q(dxcode=item.dxcode)).count() == 0:
				hosp_prescriptions_fre.append(0)
			else:
				hosp_prescriptions_fre.append(Doctor_diagnose.objects.get(Q(ordercode=item.ordercode) & Q(dxcode=item.dxcode)).frequency)
		
	sys_prescriptions = []
	disease_lists = []
	disease_list_non_duplicates = []
	sys_prescriptions_fre = []
	schWord_cnt = 0

	current_disease_max = 5
	for code in schWord.split(" "):
		#################################################################################
		# revised by khan (Dec 19. 2017)
		# sys_prescription 에 이미 저장된 내용은 networkx 결과에서 제외시켜야함
		#################################################################################

		# check if prescription exists (if not, continue)
		if Prescription.objects.filter(ordercode=code).count() != 1:
			continue
		sys_prescription = Prescription.objects.get(ordercode=code)
		schWord_cnt += 1

		# get notice
		if Notice.objects.filter(ordercode=code).count() == 1:
			notice = Notice.objects.get(ordercode=code)
			print("Notice: ", notice)
			
			if notice.display_condition:

				# 현재 병원 추천 갯수 파악
				hosp_prescription_cnt = 0
				for hosp_prescription in hosp_prescriptions:
					if hosp_prescription.ordercode == code:
						hosp_prescription_cnt += 1

				extra_system_prescription_cnt = 5 - hosp_prescription_cnt

				# get disease list from model
				disease_list = NNmodel.get_disease(ordercode_input=code, num=10)
				print("hosp_prescription: ")
				for item in hosp_prescriptions:
					print(item.dxcode)

				for disease in disease_list:
					print("disease: ", disease)
					exist = 0
					# duplicate 이 있는지 확인
					for hosp_prescription_item in hosp_prescriptions:
						if (disease[0] == hosp_prescription_item.dxcode):
							exist = 1
							break
					# duplicate 가 없으면 계속 진행
					if exist == 0:
						# 남은 시스템 추천 항목 갯수 만큼 배열에 입력
						if extra_system_prescription_cnt > 0:
							disease_list_non_duplicates.append(disease)
							print(disease[0], " added")

							# 같은 배열의 크기를 위한 작업 (zip을 위해서)
							sys_prescriptions.append(sys_prescription)

							# extra_system_prescription_cnt 1 감소
							extra_system_prescription_cnt -= 1

				for item in disease_list:
					if Doctor_diagnose.objects.filter(Q(ordercode=code) & Q(dxcode=item[0])).count() == 0:
						item.append(0)
					else:
						item.append(Doctor_diagnose.objects.get(Q(ordercode=code) & Q(dxcode=item[0])).frequency)

		else:
			print("No dxcode " + code + " in notice!!")

	print("sys_prescription: ", sys_prescriptions)
	print("sys_disease_list: ", disease_list_non_duplicates)

	context = {}
	context['schword'] = schWord
	context['schword_cnt'] = schWord_cnt
	context["search_prescription_list"] = zip(np.arange(1, 1 + len(search_prescription_list)).tolist(), search_prescription_list)
	context["hosp_prescriptions"] = zip(hosp_prescriptions, hosp_disease_name_list, hosp_prescriptions_fre)
	context["sys_prescriptions"] = zip(sys_prescriptions, disease_list_non_duplicates)

	return render(request, 'userservice.html', context)

@login_required
def check_diagnose(request):
	#if request.method == 'POST':
	return render(request, 'userservice.html')

@login_required
def updatemodel(request):

	if request.method == 'POST':
		if request.POST.get('remodel') is not None:
			t = threading.Thread(target=remodel)
			t.daemon = True
			t.start()
			time.starttime = datetime.now()
			time.status = True
			time.save()		
		else:
			form = UploadFileForm(request.POST, request.FILES)
			if form.is_valid():
				form.save()
				
				context = {}
				context['form'] = form
				context['modeling_status'] = RemodelTime.objects.latest('endtime').status
				context['last_modeling_time'] = RemodelTime.objects.latest('endtime').endtime

				return render(request, 'update_model.html', context)
			else:
				return render(request,'update_model.html')
	
	context = {}
	context['modeling_status'] = RemodelTime.objects.latest('endtime').status
	context['last_modeling_time'] = RemodelTime.objects.latest('endtime').endtime

	return render(request, 'update_model.html', context)

def remodel():
	print("Remodel start")

	datafiles = UploadFileModel.objects.filter(Q(usedflag=False))	
	for datafile in datafiles:
		df = pd.read_csv(str(datafile.file.path), sep=',', encoding='utf-8')
		print("Success reading")
		print(df)
		for _, item in df.iterrows():
			newdis = Disease(
					dxcode = item.dxcode,
					prescriptionlist = item.prescriptionlist,
					frequency = item.frequency,
					fileflag = True
				)
			newdis.save()
		datafile.usedflag = True
		datafile.save()


	newNNmodel = NeuralNetwork()
	newNNmodel.make_model()
	newNXmodel = NetworkX()
	newNXmodel.make_model()
	newNXmodel.whole_graph()

	print("Remodeling done")
	time.endtime = datetime.now()
	time.status = False
	time.save()

	NNmodel = newNNmodel
	NXmodel = newNXmodel

class m4876_00(TemplateView):
	template_name = 'm4876.html'

class m4876_01(TemplateView):
	template_name = 'm4876_01.html'

