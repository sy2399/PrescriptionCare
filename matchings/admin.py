from django.contrib import admin
from matchings.models import Disease, Prescription, Prescription_List

# Register your models here.

admin.site.register(Disease)
admin.site.register(Prescription)
admin.site.register(Prescription_List)
