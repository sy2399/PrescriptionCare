from django.shortcuts import redirect, render

from django.views.generic.base import TemplateView
from django.views.generic.edit import CreateView
from django.contrib.auth.forms import UserCreationForm
from django.core.urlresolvers import reverse_lazy

from PrescriptionCare.forms import UserCreateForm

class HomeView(TemplateView):
	template_name ='home.html'

class UserCreateView(CreateView):
	template_name = 'registration/register.html'
	form_class = UserCreationForm
	success_url = reverse_lazy('register_done')

def createuser(request):
	if request.method == 'POST':
		form = UserCreateForm(request.POST)

		if form.is_valid():
			user = form.save()
			user.refresh_from_db()
			user.userprofile.phone_num = form.cleaned_data.get('phone_num')
			user.userprofile.customer = form.cleaned_data.get('customer')
			user.userprofile.assigned_group = form.cleaned_data.get('assigned_group')
			user.userprofile.assigned_group_position = form.cleaned_data.get('assigned_group_position')
			user.userprofile.contract_start_date = form.cleaned_data.get('contract_start_date')
			user.userprofile.contract_end_date = form.cleaned_data.get('contract_end_date')
			user.userprofile.note = form.cleaned_data.get('note')
			user.save()
						
	else:
		form = UserCreateForm()

	return render(request, 'registration/register.html', {'form': form})


class UserCreateDone(TemplateView):
	template_name = 'registration/register_done.html'

