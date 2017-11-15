from django.contrib import admin
from matchings.models import Disease, Prescription, Disease_name

# Register your models here.

admin.site.register(Disease)
admin.site.register(Prescription)
admin.site.register(Disease_name)
