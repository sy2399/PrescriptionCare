from django import forms

class MatchForm(forms.Form):
	match_word = forms.CharField(label='Match Prescriptions')

