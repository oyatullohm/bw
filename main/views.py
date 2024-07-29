from django.shortcuts import render , redirect ,get_object_or_404
from django.conf import settings
from django.views import View
from .models import *
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required



class HomeView(LoginRequiredMixin,View):
    login_url = settings.LOGIN_URL
    def get(self,request):
        return render (request , 'index.html')



class TeacherView(LoginRequiredMixin,View):
    login_url = settings.LOGIN_URL
    def get(self,request) :
        company_id = request.user.company.id
        teacher = Teacher.objects.filter(company_id=company_id)\
                    .prefetch_related('salaries', 'group_teachers','group_helpers')
        context = {
            'teacher':teacher,
            'type':Teacher.TYPE
        }
        return render (request , 'teacher-all.html',context)
    
class TeacherDetailView(LoginRequiredMixin,View):
    login_url = settings.LOGIN_URL
    def get(self,request,pk) :
        company_id = request.user.company.id
        teacher = get_object_or_404(Teacher, id=pk)
        group = Group.objects.filter(company_id=company_id, teacher=teacher) | Group.objects\
            .filter(company_id=company_id,helper=teacher)\
            .select_related('teacher','helper','children')
        other_groups = Group.objects.exclude(pk__in=group).select_related('teacher','helper')
        type = Teacher.TYPE
        context = {
            'teacher':teacher,
            'group':group,
            'other_groups':other_groups,
            'type':type,
        }
        return render (request , 'teacher.html',context)
    
    def post(self,request,pk):
        username = request.POST.get('username')
        phone = request.POST.get('phone')
        type = request.POST.get('type')
        group = request.POST.get('group')
        payment = request.POST.get('payment')
        salary = request.POST.get('salary')
        child = request.POST.get('child')
        active = request.POST.get('active')
        user = get_object_or_404(Teacher, id=pk)
        user.username = username
        user.phone = phone
        user.type = type
        user.is_payment = payment == 'on' 
        user.is_salary = salary == 'on' 
        user.is_child = child  == 'on' 
        user.is_active = active == 'on'
        user.save()
        group =  get_object_or_404(Group, id=group)
        if int(user.type) == 2:

            if Group.objects.filter(teacher=user).exists():
                group_teachers = user.group_teachers
                group_teachers.teacher = None
                group_teachers.save()
            group.teacher = user
            group.save()
        if int(user.type) == 3:
            if Group.objects.filter(helper=user).exists():
                group_helpers = user.group_helpers
                group_helpers.helper = None
                group_helpers.save()
            group.helper = user
            group.save()
        return redirect (f'/teacher/{pk}/')
@login_required
def password(request,pk):
        password = request.POST.get('password')
        user = get_object_or_404(Teacher, id=pk)
        user.set_password(password)
        user.save()
        return redirect (f'/teacher/{pk}/')
@login_required
def add_teacher(request):
    
    return redirect ('/teacher')
        