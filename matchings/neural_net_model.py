import datetime
import re

from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.svm import LinearSVC, SVC
from sklearn.ensemble import AdaBoostClassifier, RandomForestClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.multiclass import OneVsRestClassifier
from sklearn.preprocessing import MultiLabelBinarizer
from sklearn.metrics import f1_score, accuracy_score, precision_score, recall_score, confusion_matrix, classification_report
from sklearn.cross_validation import train_test_split


from keras.models import Sequential
from keras.layers.core import Dense, Dropout, Activation, Flatten
from keras.callbacks import EarlyStopping
import pandas as pd, numpy as np
from keras.utils.np_utils import to_categorical
from keras.models import model_from_json
import keras
import tensorflow as tf

import pickle
import joblib
import h5py
from keras.models import model_from_json

from matchings.models import Disease, Disease_name

# get data
diseasedf = pd.DataFrame(list(Disease.objects.all().values('dxcode', 'prescriptionlist', 'frequency')))
diseasedf = diseasedf.dropna(how="any")

thres_diseasedf = diseasedf[diseasedf.frequency > 1000]

diseasenamedf = pd.DataFrame(list(Disease_name.objects.all().values('icdcode', 'namek') ))

def get_data():
	diseasedf = pd.DataFrame(list(Disease.objects.all().values('dxcode', 'prescriptionlist', 'frequency')))
	diseasedf = diseasedf.dropna(how="any")

	thres_diseasedf = diseasedf[diseasedf.frequency > 1000]

	diseasenamedf = pd.DataFrame(list(Disease_name.objects.all().values('icdcode', 'namek') ))



class Vectorization:

	pattern = "(?u)\\b[\\w-]+\\b"

	def tfidffVectorization():
		vect = TfidfVectorizer()
		return vect

	def countVectorization():
		vect = CountVectorizer()
		return vect

	def W2Vectorization(X_list, y):
		disease_docs = W2V.construct_docs(X_list,range(len(y)))
		doc2vec_model = W2V.run_doc2vec(disease_docs)
		vect = W2V.get_vectors(doc2vec_model, range(len(y)))
		return vect


class MachineLearningModeling:
	def __init__(self, model_type, X, y, test_size):
		if model_type == "LR":
			self.model = OneVsRestClassifier(LogisticRegression(penalty='l2', tol=0.0001, C=1))
		elif model_type == "RF":
			self.model = OneVsRestClassifier(RandomForestClassifier(n_estimators=50))
		elif model_type == "SVM":
			self.model = OneVsRestClassifier(SVC(C=1000, probability=True, kernel='rbf', gamma=0.001))

		self.X_train, self.X_test, self.y_train, self.y_test = train_test_split(X, y, test_size=test_size, random_state=0)
		self.fit_model(self.X_train, self.y_train)
		self.predict_model_top(self.X_test, self.y_test)
		self.predict_model_range(self.X_test, self.y_test, self.y_train, 10)


	def fit_model(self, X_train, y_train):  
		self.model.fit(X_train, y_train)

	def predict_model_top(self, X_test, y_test):
		y_pred = self.model.predict(X_test)
		accuracy_score(y_test, y_pred)

		# it basically returns the same accuracy result
		count = 0
		for i in range(0,len(y_test)):
			if (y_test[i][0] in y_pred[i]):
				count += 1

	def predict_model_range(self, X_test, y_test, y_train, num):
		y_probs = self.model.decision_function(X_test)

		all_classes = np.array(list(set(y_train.ravel())))
		all_classes[np.argmax(y_probs, axis=1)]
		all_classes = np.array(list(set(y_train.ravel())))
		all_classes = all_classes[all_classes.argsort()]
		all_classes[np.argmax(y_probs, axis=1)]

		count = 0
		for i in range(0,len(y_test)):
			top_index = np.argsort(y_probs[i])[::-1][:num] # find the index of top 'num' values
			top_diagnosis = all_classes[top_index]

			if (y_test[i] in top_diagnosis):
				count += 1


class NeuralNetwork:
	def __init__(self):

		try:
			with open("static/NNmodel_data/y_classes.txt", 'r') as y:
				self.y_classes = y.read().splitlines()
			print("y_classes Checked")

			vectorizer = joblib.load("static/NNmodel_data/vectorizer.pkl")
			print("vetorizer Checked")
		
			self.vect = vectorizer

			json_file = open("static/NNmodel_data/NN_model.json", "r")
			print("json Checked")
			loaded_NN_model_json = json_file.read()
			json_file.close()

			loaded_model = model_from_json(loaded_NN_model_json)

			loaded_model.load_weights("static/NNmodel_data/NN_model.h5")
			print("h5 Checked")
	
			self.graph = tf.get_default_graph()
			self.model = loaded_model
			print("NN: Files loaded successfully")

		except:
			print("NN: DO not have required files")
			self.make_model()			
		
	def make_model(self):
		print("NN: making new model")
		
		get_data()

		X = thres_diseasedf[["dxcode"]]
		y = thres_diseasedf[["prescriptionlist"]]

		X_list = X.values.ravel()
		num_features = len(set("".join(X_list[0:len(X_list) + 1])))
		
		self.vect = Vectorization.tfidffVectorization()

		self.vect.fit(X_list)
		X_vect = self.vect.transform(X_list)

		#Training and Testing Data Preparation
		self.X_train, self.X_test, self.y_train, self.y_test = train_test_split(X_vect, y.values, test_size=0.10, random_state=0)
		
		self.y_classes = list(set(y.values.ravel()))
		self.y_train_idx = []

		for item in self.y_train:
			self.index = self.y_classes.index(item)
			self.y_train_idx.append(self.index)

		callback1 = keras.callbacks.EarlyStopping(monitor='val_loss', patience=3)
		self.train_and_fit_model(self.X_train, self.y_train_idx, self.y_classes, 100, 100, 0.1, [callback1])

		######################################################
		#	save model as file
		######################################################
		with open("static/NNmodel_data/vectorizer.pkl", "wb") as handle:
			joblib.dump(self.vect, handle, compress=True)

		y_class_file = open('static/NNmodel_data/y_classes.txt', 'w')

		for item in self.y_classes:
			y_class_file.write("%s\n" % item)

		NN_model_json = self.model.to_json()
		with open("static/NNmodel_data/NN_model.json", "w") as json_file:
			json_file.write(NN_model_json)
	
		self.model.save_weights("static/NNmodel_data/NN_model.h5")

	# construct model
	def build_neural_net(self, X_train, y_classes):
		self.model = Sequential()
		self.model.add(Dense(2056, input_shape=(X_train.shape[1],)))
		self.model.add(Activation('relu'))
		self.model.add(Dropout(0.1))
		self.model.add(Dense(1024))
		self.model.add(Activation('relu'))
		self.model.add(Dropout(0.1))
		self.model.add(Dense(len(y_classes)))
		self.model.add(Activation('softmax'))

		self.model.compile(
			loss='sparse_categorical_crossentropy',
			optimizer='sgd',
			metrics=['accuracy']
		)

	#train model
	def train_and_fit_model(self, X_train, y_train_idx, y_classes, b_size, e_size, v_split, callback_func):
		self.build_neural_net(X_train, y_classes)
		hist = self.model.fit(X_train.toarray(), 
								np.array(y_train_idx),
								batch_size = b_size,
								epochs=e_size,
								validation_split=v_split,
								callbacks=callback_func,
								verbose=1)		
		self.graph = tf.get_default_graph()

	def get_disease(self, ordercode_input, num):
		ordercode_input_list = []
		ordercode_input_list.append(ordercode_input)

		#원하는 처방 값을 X_list 에 넣기
		ordercode_vect = self.vect.transform(ordercode_input_list)
		with self.graph.as_default():
			y_pred = self.model.predict(ordercode_vect.toarray())

			all_classes = np.array(self.y_classes)
			all_classes[np.argmax(y_pred, axis=1)]

			for i in range(0, len(y_pred)):
				top_index = np.argsort(y_pred[i])[::-1][:num]# find the index of top ?? value
				top_diagnosis = all_classes[top_index]

			selected_results = top_diagnosis.tolist()

			results_converted_to_list = []
			for i in range(0, len(top_diagnosis)):
				code = top_diagnosis[i].split(" ")[0]
				if i > 4:
					relation = 'High'
				else:
					relation = 'Very High'
			
				if (diseasenamedf['icdcode'] != code).all():
					code_name = "Unknown"
				else:
					idx = diseasenamedf['icdcode'][diseasenamedf['icdcode'] == code].index[0]
					code_name = diseasenamedf['namek'][idx]

				item = []
				item.append(code)
				item.append(code_name)
				item.append(relation)

				results_converted_to_list.append(item)
			
			return results_converted_to_list


