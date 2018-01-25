####################################################
#		forms
####################################################

from django import forms

from userprofile.models import UserProfile

class UserProfileForm(forms.ModelForm):
	class Meta:
		model = UserProfile
		fields = ('username', 'password1', 'password2', 'first_name', 'email', 'phone_num', 'customer', 'assigned_group', 'assigned_group_position', 'contract_start_date', 'contract_end_date', 'note',)
