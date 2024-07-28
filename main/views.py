from django.shortcuts import render
from django.conf import settings
from django.views import View
from .models import *
from django.contrib.auth.mixins import LoginRequiredMixin




class HomeView(LoginRequiredMixin,View):
    login_url = settings.LOGIN_URL
    def get(self,request):
        return render (request , 'index.html')



class TeacherView(LoginRequiredMixin,View):
    login_url = settings.LOGIN_URL
    def get(self,request) :
        company_id = request.user.company.id

        teacher = Teacher.objects.filter(company_id=company_id)
        context = {
            'teacher':teacher,
        }
        return render (request , 'teacher-all.html',context)
    
# class TeacherView(View):
#     def get(self,request):
#         company_id = request.user.company.id
#         return render (request , 'teacher-all.html')