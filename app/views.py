from django.shortcuts import render
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token
from rest_framework.views import APIView
from rest_framework.permissions import  AllowAny , IsAuthenticated
from rest_framework.response import Response
from main.models import Teacher , Tarif, Company
from .serializer import *
from django.utils import timezone
from datetime import timedelta

# Create your views here.
class LoginApiView(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        username = request.data['username']
        password = request.data['password']
        user = authenticate(username=username, password=password)
        if user:
            token, created = Token.objects.get_or_create(user=user)
            # if user.master or user.driver or user.agent :
            return Response({'success': True, 'token': token.key,'user':TeacherSerializer(user,many=False).data})
            # return Response({'success': False, 'error': 'telefon raqam yoki parol noto`g`ri !'})
        return Response({'status': False})


class  RegisterApiView(APIView):
    permission_classes = [AllowAny]
    def post(self,request):
        data = request.data 
        company = data['company']
        username = data['username']
        phone = data['username']
        password = data['password']
        password_2 = data['password_2']
        try:
            if password == password_2:
                tarif = Tarif.objects.get(name='standart')
                company = Company.objects.create(tarif=tarif,name=company,
                                             phone=phone,start_date=timezone.now(),
                                             end_date=timezone.now()+timedelta(days=30))
                Teacher.objects.create_user(
                    company=company,
                    username=username,
                    phone=phone,
                    type = 1,
                    is_payment = True,
                    is_salary = True,
                    is_child = True, 
                    is_main  = True,
                    password=password)
                return Response({'success': True,} )
        except:
            return Response({'success': False,'message': 'username band yoki parollar bir hil emas ',} )
        return Response({'success': False,} )

class HomeApiView(APIView): 

    permission_classes = [AllowAny]
    def get(self, request,):
        return Response({"status":"ok"})