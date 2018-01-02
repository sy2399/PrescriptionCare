from django import forms
from .models import UploadFileModel

class MatchForm(forms.Form):
	match_word = forms.CharField(label='Match Prescriptions')

class UploadFileForm(forms.ModelForm):
	class Meta:
		model = UploadFileModel;
		fields = ('title', 'file')

	def __init__(self, *args, **kwargs):
		super(PostForm, self).__init__(*args, **kwargs)
		self.fields['file'].required = False