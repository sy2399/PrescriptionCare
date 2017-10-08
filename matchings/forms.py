from django import forms

class DiseaseSearchForm(forms.Form):
	search_word = forms.CharField(label='Search Prescriptions')
