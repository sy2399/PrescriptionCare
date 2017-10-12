from django.db import models

import numpy as np
import pandas as pd
import datetime 


# Create your models here.

class Disease(models.Model):	
	#차트번호
	PTNO = models.IntegerField(default=0) 
	
	#상병시작일자
	STARTDATE = models.CharField(max_length=1)
	
	#상병종료일자
	ENDDATE = models.CharField(max_length=1)	
	
	#외래, 입원
	IPDOPD = models.CharField(max_length=1) 
	
	#과코드
	DEPTCODE = models.CharField(max_length=1024)

	#입력과
	WRITEDEPT = models.CharField(max_length=1024) 
	
	#입력의사
	WRITEDRCODE = models.IntegerField(default=0) 	
	
	#증상, 질병
	DXCODE = models.CharField(max_length=1024)
	
	#특정기호
	SPCKIHO = models.CharField(max_length=1024)

	#증상, 부상병
	PRESENTSYMTOM = models.IntegerField(default=0)	
	
	#추가정보
	DXMOREFLAG = models.IntegerField(default=0) 	
	
	#처방코드
	PRESCRIPTIONLIST = models.CharField(max_length=4096) 


class Prescription(models.Model):
	#차트번호
	PTNO = models.IntegerField(default=0)	

	#처방일자
	ORDERDATE = models.DateTimeField('order date') 	

	#외래, 입원
	IPDOPD = models.CharField(max_length=1) 	

	#과코드
	DEPTCODE = models.CharField(max_length=1024) 	

	#처방구분
	ORDERCLASS = models.IntegerField(default=0) 	

	#처방그룹
	ORDERGROUP = models.IntegerField(default=0) 	

	#처방전번호
	SLIPNUM = models.IntegerField(default=0) 	

	#수가분류코드
	BUN = models.IntegerField(default=0) 	

	#수가세분류코드
	BUNDETAIL = models.IntegerField(default=0) 	

	#처방코드
	ORDERCODE = models.CharField(max_length=1024) 	

	#처방명
	ORDERNAME = models.CharField(max_length=1024) 	

	#처방수가코드
	SUCODE = models.CharField(max_length=1024) 	

	#보험코드
	BCODE = models.CharField(max_length=1024) 	
	
	#보험구분코드
	SELFFLAG = models.IntegerField(default=0)  

class Prescription_List(models.Model):
	ORDERCODE = models.CharField(max_length=128)

	def input_code(self):
		dxcode_input.append(self.ORDERCODE)

class Prescription_Temp(models.Model):
	IPDOPD = models.CharField(max_length=1024) 
	DXCODE = models.CharField(max_length=1024) 
	ORDERCLASS = models.CharField(max_length=1024) 
	ORDERCODE = models.CharField(max_length=1024) 
	ORDERNAME = models.CharField(max_length=1024) 
	DXCODECOUNT = models.IntegerField(default=0) 
	DATECOUNT = models.IntegerField(default=0) 
