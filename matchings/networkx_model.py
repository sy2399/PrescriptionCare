import math
import pandas as pd
import numpy as np
import random
from networkx import *
from networkx.readwrite import json_graph
import networkx as nx
from networkx.algorithms import approximation as approx
from networkx.algorithms.approximation import clique
from itertools import combinations
from collections import Counter
import operator

import json
import time

from matchings.models import Disease, Disease_name, Prescription

# get data
diseasedf = pd.DataFrame(list(Disease.objects.all().values('dxcode', 'prescriptionlist') ))
diseasenamedf = pd.DataFrame(list(Disease_name.objects.all().values('icdcode', 'namek') ))

prescriptiondf = pd.DataFrame(list(Prescription.objects.all().values('ordercode', 'ordername')))
tls = []
for item in prescriptiondf['ordercode'].str.split(" "):
	tls.append(item[0])
prescriptiondf['ordercode'] = pd.Series(data = tls)

# drop rows which contain nan

class NetworkX:
	def __init__(self):

		try:
			#read jsonfile

			#for seperating main/sub disease
#			if import_flag == 1:
#				json_file = open("static/main_NX_model.json", "r")
#			elif import_flag == 2:
#				json_file = open("static/sub_NX_model.json", "r")


			#for non seperating main/sub disease
			json_file = open("static/NXmodel_data/NX_model.json", "r")

			loaded_NX_model_json= json.load(json_file)
			json_file.close()

			self.G = json_graph.node_link_graph(loaded_NX_model_json)

			print("NX: File loaded successfully")

		except:
			print("NX: Do not have required files")
			#tempdf = df[df.주부상병 == import_flag]
				
			X_list, y_list = self.create_input_list(diseasedf)
				
			edges = {}
			for i in range(len(X_list)):
				dxcode = X_list[i].strip().split(" ")
				disease = y_list[i]
				
				for j in dxcode:
					edge = disease + " " + j
					if edge not in edges: edges[edge] = 1
					else: edges[edge] += 1

			edge_data = pd.DataFrame(columns=['source', 'target', 'edge_count'], index=np.arange(len(edges)))

			i = 0
			for edge in edges.keys():
				s, t = edge.split(' ')
				edge_data['source'][i] = s
				edge_data['target'][i] = t
				edge_data['edge_count'][i] = edges[edge]
				i= i+1

			source = {}
			for index, row in edge_data.iterrows():
				if row['source'] not in source: 
					source[row['source']] = row['edge_count'] 
				else:
					source[row['source']] += row['edge_count']

			source_count = pd.DataFrame([source]).T
			source_count.columns = ['source_count']
			edge_df = edge_data.join(source_count, how='inner', on='source', sort=True)
			edge_df = edge_df.sort_index()

			DG = nx.DiGraph()

			for index, row in edge_df.iterrows():
				DG.add_weighted_edges_from([(row['source'], row['target'], float(row['edge_count']))]) 
				#modify to row['edge_count'] /row['source_count'] if radio mode

			self.G = DG.to_undirected()

			JG = json_graph.node_link_data(self.G)
			str_json = json.dumps(JG)

			# for seperating main/sub disease
#			if import_flag == 1:
#				with open("static/NXmodel_data/main_NX_model.json", "w") as json_file:
#					json_file.write(str_json)
#			elif import_flag == 2:
#				with open("static/sub_NX_model.json", "w") as json_file:
#					json_file.write(str_json)	


			#for non seperating main/sub disease
			with open("static/NXmodel_data/NX_model.json", "w") as json_file:
				json_file.write(str_json)	

			json_file.close()


	## used for init
	def create_input_list(self, df):
		prev_main_disease_code = ""
		diagnosis_list = ""
		X_list = []
		y_list = []

		for index, row in df.iterrows():
			main_disease_code = row['dxcode'].strip()
			diagnosis_code = row['prescriptionlist'].strip().replace("\n","")

			if (index == 0):
				diagnosis_list += diagnosis_code + " "
			else:
				if (prev_main_disease_code != main_disease_code):
					if (len(diagnosis_list) != 0):
						X_list.append(diagnosis_list)
						y_list.append(prev_main_disease_code)

					diagnosis_list = "" # initialize
					diagnosis_list += diagnosis_code + " "
				else:
					diagnosis_list += diagnosis_code + " "

			prev_main_disease_code = main_disease_code

		return X_list, y_list


	#function to get disease
	def find_disease(self, dxcode_input):
		cnt = len(dxcode_input)
		neighbors = []
		for dxcode in dxcode_input:
			neighbors += self.G.neighbors(dxcode) 
		neighbors = list(set(neighbors))
		
		disease_weight = {}
		for n in neighbors:
			disease_weight[n] = {'count':0,'weight':0}
			for dxcode in dxcode_input:
				if n in self.G.neighbors(dxcode):
					disease_weight[n]['count'] += 1
					disease_weight[n]['weight'] += self.G[n][dxcode]['weight'] 
		
		return sorted(disease_weight.items(), key=lambda x:(x[1]['count'], x[1]['weight']), reverse=True)



	#function to get dxcode
	def find_dxcode(self, disease):
		return list(self.G.neighbors(disease))


	##function for searching
	def get_dxcode_input_list(self, dxcode_input):
		dxcodes = dxcode_input.split(" ")

		dxcode_input_list = []
		for dxcode in dxcodes:
			dxcode_input_list.append(dxcode)

		return dxcode_input_list

	def get_disease(self, dxcode_input, num):

		dxcode = self.get_dxcode_input_list(dxcode_input)
		results = list(self.find_disease(dxcode))
		
		result_len = len(results)
		selected_results = results[0:num]

		results_converted_to_list = []
		for item in selected_results:
			results_converted_to_list.append(list(item))

		#make proportion field in results
#		total_count = 0
#		for item in results_converted_to_list:
#			total_count = total_count + item[1]['count']

		start = int(round(time.time() * 1000))
		rank = 0
		for item in results_converted_to_list:
			percentage = rank/result_len
			rank = rank + 1
			if percentage < 0.2:
				relation = "Very high"
			elif percentage < 0.4:
				relation = "High"
			elif percentage < 0.6:
				relation = "Middle"
			elif percentage < 0.8:
				relation = "Low"
			else:
				relation = "Very Low"

			#item[1]['proportion'] = item[1]['count'] / total_count
			item.append(relation)


		#map disease name
		for item in results_converted_to_list:
			idx = diseasenamedf['icdcode'][diseasenamedf['icdcode'] == item[0]].index[0]
			item[1] = diseasenamedf['namek'][idx]
		
#		for item in results_converted_to_list:
#			#map prescription name
#			prescription_list = []
#			for ordercode in self.find_dxcode(item[0])[:num]:
#				flag = False
#				for idx, j in prescriptiondf.iterrows():
#					dict_for_order = {}
#
#					if ordercode.split(" ") == j['ordercode'].split(" "):
#						dict_for_order = {'ordercode': ordercode, 'ordername': j['ordercode']}
#						flag = True
#						break
#
#				if flag is False:
#					dict_for_order = {'ordercode': ordercode, 'ordername': "Unknown"}
#				prescription_list.append(dict_for_order)
#
#			item.append(prescription_list)

		for item in results_converted_to_list:
			prescription_code_list = []
			for prescription_code in self.find_dxcode(item[0])[:num]:
				prescription_code_list.append(prescription_code)


			item.append(prescription_code_list)

		for item in results_converted_to_list:
			prescription_name_list = ["Unknown"]
			for i in np.arange(num):

				if (prescriptiondf['ordercode'] != item[3][i]).all():
					continue
				
				idx = prescriptiondf['ordercode'][prescriptiondf['ordercode'] == item[3][i]].index[0]
				prescription_name_list.append(prescriptiondf['ordername'][idx])

			item.append(prescription_name_list)

		return results_converted_to_list

