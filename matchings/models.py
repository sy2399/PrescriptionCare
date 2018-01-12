from django.db import models

class Disease(models.Model):	
	dxcode = models.CharField(max_length=1024)
	prescriptionlist = models.CharField(max_length=4096) 
	frequency = models.IntegerField(default=1)
	fileflag = models.BooleanField(default=True)

class Prescription(models.Model):
	ordercode = models.CharField(max_length=128)
	ordername = models.CharField(max_length=1024)

class Disease_name(models.Model):
	icdcode = models.CharField(max_length=1024)
	fullcode = models.CharField(max_length=1024)
	namek = models.CharField(max_length=1024)
	namee = models.CharField(max_length=1024)

class Notice(models.Model):
	ordercode = models.CharField(max_length=128) # 처방 코드
	ordername = models.CharField(max_length=1024) # 처방 이름
	notice_description = models.CharField(max_length=1024) # 노티스 내용
	display_condition = models.BooleanField(max_length=1) # 0: 채크된 진단명만 진료화면에 노출함, 1: 모든 진단명을 노출함

class Doctor_diagnose(models.Model):
	ordercode = models.CharField(max_length=128) # 처방 코드
	dxcode = models.CharField(max_length=1024) # 상병 코드
	frequency = models.IntegerField(default=0) # 처방-상병 관계 빈도수 (사용빈도 값을 위해 사용될 예정)

class Review(models.Model):
	ordercode = models.CharField(max_length=128) # 처방 코드
	dxcode = models.CharField(max_length=1024) # 상병 코드
	frequency = models.IntegerField(default=1) # 처방-상병 관계 빈도수 (실제로는 많이 안쓰일 수도 있음)

class UploadFileModel(models.Model):
    title = models.TextField(default='') # 업로드한 파일명
    file = models.FileField(null=True) # 업로드한 파일
