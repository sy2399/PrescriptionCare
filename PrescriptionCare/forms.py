from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

# class DateInput(forms.DateInput):
# 	input_type = 'date'

class UserCreateForm(UserCreationForm):
	first_name = forms.CharField(max_length=30, help_text="Required")
	email = forms.EmailField(max_length=256, help_text="Required")
	ACTIVE = (
		(True, 'Active'),
		(False, 'Inactive')
	)
	
	#is_active = forms.BooleanField(required=False)
	is_active = forms.ChoiceField(choices=ACTIVE, label="계정 상태", initial='', widget=forms.Select(), required=True)

	phone_num = forms.CharField(max_length=20, help_text="Required")
	customer = forms.CharField(max_length=256, help_text="Required")
	assigned_group = forms.CharField(max_length=256, required=False, help_text="Optional")
	assigned_group_position = forms.CharField(max_length=256, required=False, help_text="Optional")
	contract_start_date = forms.DateField(help_text="Required")
	contract_end_date = forms.DateField(help_text="Required")
	note = forms.CharField(required=False, help_text="Optional", widget=forms.Textarea)

	class Meta:
		model = User
		fields = ('username', 'password1', 'password2', 'first_name', 'email', 'is_active','phone_num', 'customer', 'assigned_group', 'assigned_group_position', 'contract_start_date', 'contract_end_date', 'note',)

	def save(self, commit=True):
		user = super(UserCreateForm, self).save(commit=False)
		user.phone_num = self.cleaned_data["phone_num"]
		user.customer = self.cleaned_data["customer"]
		user.assigned_group = self.cleaned_data["assigned_group"]
		user.assigned_group_position = self.cleaned_data["assigned_group_position"]
		user.contract_start_date = self.cleaned_data["contract_start_date"]
		user.contract_end_date = self.cleaned_data["contract_end_date"]
		user.note = self.cleaned_data["note"]
		
		if commit:
			user.save()

		return user
