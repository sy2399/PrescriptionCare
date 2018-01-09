from django.contrib import admin
from matchings.models import Disease, Prescription, Disease_name, Review, Notice, Doctor_diagnose, UploadFileModel

# Register your models here.

admin.site.register(Disease)
admin.site.register(Prescription)
admin.site.register(Disease_name)
admin.site.register(Review)
admin.site.register(Notice)
admin.site.register(Doctor_diagnose)
admin.site.register(UploadFileModel)

