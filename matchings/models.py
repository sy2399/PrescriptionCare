from django.db import models

# Create your models here.

class Disease(models.Model):	
	dxcode = models.CharField(max_length=1024)
	prescriptionlist = models.CharField(max_length=4096) 

class Prescription(models.Model):
	ordercode = models.CharField(max_length=128)
	ordername = models.CharField(max_length=1024)

class Disease_name(models.Model):
	icdcode = models.CharField(max_length=1024)
	fullcode = models.CharField(max_length=1024)
	namek = models.CharField(max_length=1024)
	namee = models.CharField(max_length=1024)
