import math
import pandas as pd
import numpy as np
import random
from networkx import *
import networkx as nx
from networkx.algorithms import approximation as approx
from networkx.algorithms.approximation import clique
from itertools import combinations
from collections import Counter
import operator

from matchings.models import Disease

# get data
df = pd.DataFrame(list(Disease.objects.all().values('DXCODE', 'PRESCRIPTIONLIST')))

# add column names
df.columns = ["주상병", "처방코드"]

# drop rows which contain nan
df = df.dropna(how="any")

diagnosis_code_list = df.처방코드.unique()# loop dataframe

class NetworkxModel():

	def create_input_list(df):
		prev_main_disease_code = ""
		diagnosis_list = ""
		X_list = []
		y_list = []

		for index, row in df.iterrows():
			main_disease_code = row['주상병'].strip()
			diagnosis_code = row['처방코드'].strip().replace("\n","")

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
	def find_disease(self, Graph, dxcode_input):
		cnt = len(dxcode_input)
		neighbors = []
		for dxcode in dxcode_input:
			neighbors += Graph.neighbors(dxcode) 
		neighbors = list(set(neighbors))
		
		disease_weight = {}
		for n in neighbors:
			disease_weight[n] = {'count':0,'weight':0}
			for dxcode in dxcode_input:
				if n in Graph.neighbors(dxcode):
					disease_weight[n]['count'] += 1
					disease_weight[n]['weight'] += Graph[n][dxcode]['weight'] 
		
		return sorted(disease_weight.items(), key=lambda x:(x[1]['count'], x[1]['weight']), reverse=True)

	#function to get dxcode
	def find_dxcode(Graph, disease):
		print(Graph.neighbors(disease))

	def get_dxcode_input_list(self, dxcode_input):
		dxcodes = dxcode_input.split(" ")

		dxcode_input_list = []
		for dxcode in dxcodes:
			dxcode_input_list.append(dxcode)

		return dxcode_input_list

	def get_disease_by_networkx(self, dxcode_input):

		dxcode = self.get_dxcode_input_list(dxcode_input)
		results = self.find_disease(self.G, dxcode)[0:10]
		
		return results


	X_list, y_list = create_input_list(df)
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
		DG.add_weighted_edges_from([(row['source'], row['target'], float(row['edge_count']/row['source_count']))])

	G = DG.to_undirected()
