from django.shortcuts import render
from django.views import View
from .models import *
# Create your views here.
class HomeView(View):
    def get(self,request):
        return render (request , 'index.html')



class TeacherView(View):
    def get(self,request, pk):


        company_id = request.user.company.id
        user = Teacher.objects.get(id =pk)
        # group = Group.objects.filter(company_id=company_id)
        group = Group.objects.filter(company_id=company_id, teacher=user) | Group.objects.filter(company_id=company_id,helper=user)
        other_groups = Group.objects.exclude(pk__in=group)
        context = {
            'teacher':user,
            'group':group,
            'other_groups':other_groups,
        }
        return render (request , 'teacher.html',context)
    
# class TeacherView(View):
#     def get(self,request):
#         company_id = request.user.company.id
#         return render (request , 'teacher-all.html')