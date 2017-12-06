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



# 심사과에서 결정하는 처방-상병 관계 기록
class Review(models.Model):
	ordercode = models.CharField(max_length=128) # 처방 코드
	dxcode = models.CharField(max_length=1024) # 상병 코드
	frequency = models.CharField(max_length=16) # 처방-상병 관계 빈도수 (실제로는 많이 안쓰일 수도 있음)

# 심사과에서 결정하는 처방 notice 내용 기록
class Notice(models.Model):
	ordercode = models.CharField(max_length=128) # 처방 코드
	ordername = models.CharField(max_length=1024) # 처방 이름
	notice_description = models.CharField(max_length=1024) # 노티스 내용
	display_condition = models.CharField(max_length=1) # 0: 채크된 진단명만 진료화면에 노출함, 1: 모든 진단명을 노출함

# HIS 페이지를 통해 의사가 결정하는 내용 기록
class Doctor(models.Model):
	ordercode = models.CharField(max_length=128) # 처방 코드
	dxcode = models.CharField(max_length=1024) # 상병 코드
	frequency = models.CharField(max_length=16) # 처방-상병 관계 빈도수 (사용빈도 값을 위해 사용될 예정)

# slide 3
# 처방에 따른 상병 선택, notice, checkbox 선택 후. save 눌렀을때,
# Review table에 해당 처방, 상병 기록 여부 파악
#  - 기록 있으면 frquency += 1
#  - 기록 없으면 처방, 상병 새로 기록하고, frequency = 1
# Notice table에 해당 처방 기록 여부 파악
#  - 기록 있으면 notice_description 내용 및 display_condition 업데이트
#  - 기록 없으면 처방, notice_description, display_condition 새로 기록

# slide 11
# 사용자가 선택한 처방 (처방 선택 할 수 있는 입력 박스 필요)에 따라서
# 처방 목록과 상병 목록에 초기 결과 보여줌
# 처방 목록
#  - 처방유형: 외래
#  - 처방코드: 입력된 처방코드 가져옴
#  - 처방명: Prescription table에서 가져옴
#  - Notice: Notice table애서 가져옴
# 상병 추천: 각 처방에 따라서 상병을 보여줘야 함. display_condition 에 따라서 내용이 달라짐
#  - display_condition == 0
#     - Review table에서의 값만 보여줌
#  - display_condition == 1
#	  - Review table에서의 값과 우리 모델에서의 값을 모두 보여줌
#  - 처방이 2개 이상인 경우
#     - 처방 순서대로 병원 추천 상병을 우선 보여주고, 시스템 추천은 그 뒤로 보여줌
#  - "확인(or저장)" 버튼을 눌렀을때,
#     - 선택된 처방-상병 기록을 Doctor table에 저장
#         - 테이블에 이미 존재하면 frequency += 1
#         - 기록이 없으면 처방, 상병, frequency = 1 으로 새로 기록
#         - 기록된 내용을 바탕으로 사용빈도 값을 계산할 수 있음
