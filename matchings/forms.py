from django import forms

class PrescriptionSearchForm(forms.Form):
	search_word = forms.CharField(label='Search Prescriptions')

