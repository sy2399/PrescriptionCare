###########반드시 python3버전이 설치 되어있어야함

## install library ##
sudo apt-get install python3-pip
sudo pip3 install django==1.11
sudo pip3 install django-widget_tweaks
sudo pip3 install pandas
sudo pip3 install networkx
sudo pip3 install sklearn 
sudo pip3 install keras
sudo pip3 install tensorflow

sudo pip3 install pickle
sudo pip3 install h5py
sudo pip3 install joblib

## To create superuser account, use command below inside the project root directory:
## python3.~ manage.py createsuperuser

## To open the server,  use command below inside the project root directory:
## python3.~ manage.py runserver [addr]

## 만약 로컬에서 동작시킬 경우 addr를 입려하지 않아도 자동으로 로컬 8000번 포트에서 동작함. 
## 웹서버에 올려서 동작시키고 싶은 경우, PrescriptionCare/settings.py 에서 ALLOWED_HOSTS에 해당 서버의 주소를 입력후, addr입력 시 0.0.0.0:8000을 입력하면 서버의 8000번에서 동작함
