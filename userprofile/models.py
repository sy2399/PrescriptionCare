from django.db import models

from django.contrib.auth.models import User, Group
from django.dispatch import receiver
from django.db.models.signals import post_save

class UserProfile(models.Model):
	user = models.OneToOneField(User)
	phone_num = models.CharField(max_length=20)
	customer = models.CharField(max_length=256)
	assigned_group = models.CharField(max_length=256)
	assigned_group_position = models.CharField(max_length=256)
	contract_start_date = models.DateField(null=True, blank=True)
	contract_end_date = models.DateField(null=True, blank=True)
	note = models.CharField(max_length=256)

#def add_to_default_group(sender, **kwargs):
#	user = kwargs["instance"]
#	if kwargs["created"]:
#		group = Group.objects.get(name='f1')
#		user.groups.add(group)
#
#	post_save.connect(add_to_default_group, sender=User)

@receiver(post_save, sender=User)
def update_user_profile(sender, instance, created, **kwargs):
	if created:
		UserProfile.objects.create(user=instance)
	instance.userprofile.save()
