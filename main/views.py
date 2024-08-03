from django.shortcuts import render , redirect ,get_object_or_404
from django.conf import settings
from django.views import View
from .models import *
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from decimal import Decimal
from django.db.models import OuterRef, Subquery
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage 
from django.db.models import Count

class HomeView(LoginRequiredMixin,View):
    login_url = settings.LOGIN_URL
    def get(self,request):
        return render (request , 'index.html')



class TeacherView(LoginRequiredMixin,View):
    login_url = settings.LOGIN_URL
    def get(self,request) :
        company_id = request.user.company.id
        teacher = Teacher.objects.filter(company_id=company_id, is_active=True)\
                    .prefetch_related('group_teachers','group_helpers')
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
        tarif = TarifCompany.objects.filter(company_id=company_id,status =1)

        context = {
            'teacher':teacher,
            'group':group,
            'other_groups':other_groups,
            'type':type,
            'tarif':tarif
        }
        return render (request , 'teacher.html',context)
    
    def post(self,request,pk):
        username = request.POST.get('username')
        phone = request.POST.get('phone')
        type = request.POST.get('type')
        group = request.POST.get('group' )
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
        if int(user.type) == 2:
            group =  get_object_or_404(Group, id=group)
            if Group.objects.filter(teacher=user).exists():
                group_teachers = user.group_teachers
                group_teachers.teacher = None
                group_teachers.save()
            group.teacher = user
            group.save()
        if int(user.type) == 3:
            group =  get_object_or_404(Group, id=group)
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
def salary(request, pk):
    user = get_object_or_404(Teacher, id=pk)
    tarif =request.POST.get('tarif')
    tarif = get_object_or_404(TarifCompany, id=tarif)
    user.tarif = tarif
    user.save()
    messages.error(request, 'tarif almashdi ')
    return redirect(f'/teacher/{pk}/')
        

@login_required
def add_teacher(request):
    company = request.user.company
    if not Teacher.objects.filter(username=request.POST.get('username')).exists() \
        and  request.POST.get('password') == request.POST.get('password_2') :
        Teacher.objects.create_user(
        company = company,
        username=request.POST.get('username'),
        phone=request.POST.get('phone'),
        hired_date =timezone.now(),
        password=request.POST.get('password'),
        type = request.POST.get('type')
        )
        return redirect ('/teacher')
    messages.error(request, 'usename  band  yoki parollar birhil emass ')
    return redirect ('/teacher')


class GroupView(LoginRequiredMixin,View):
    login_url = settings.LOGIN_URL
    def get(self,request,*args, **kwargs):
        company = request.user.company 
        group =  Group.objects.filter(company=company, is_active = True)
        return render(request,'group.html',{'group':group}) 
    def post(self,request, *args, **kwargs):
        name = request.POST.get('name')
        Group.objects.create(
            name=name,
            company=request.user.company,
        )
        return redirect('/group')
    

class GroupDetailView(LoginRequiredMixin, View):
    login_url = settings.LOGIN_URL
    
    def get(self, request, pk, *args, **kwargs):
        page = request.GET.get('page')
        group = Group.objects.get(id=pk)
        children = Child.objects.filter(group=group).select_related('tarif')
        today = timezone.now().date()

        # All relevant attendance records for today
        attendances = Attendance.objects.filter(child__in=children, date=today)
        attendance_dict = {att.child_id: att for att in attendances}
        start_of_month = today.replace(day=1)

        attendance_counts = Attendance.objects.filter(
            child__in=children,
            is_active=True,
            date__gte=start_of_month,
            presence=True
        ).values('child_id').annotate(count=Count('id'))

        attendance_dict_count = {att['child_id']: att['count'] for att in attendance_counts}


        paginator = Paginator(children, 2)
        try:
            children = paginator.page(page)
        except PageNotAnInteger:
            children = paginator.page(1)
        except EmptyPage:
            children = paginator.page(paginator.num_pages)
        
        children_attendance = []
        for child in children:
            attendance = attendance_dict.get(child.id, None)
            attendance_counts = attendance_dict_count.get(child.id, 0)
            children_attendance.append({
                'child': child,
                'attendance': attendance,
                'attendance_counts':attendance_counts,
            })

        return render(request, 'group-detail.html', {'group': group, 'children_attendance': children_attendance, 'paginator': paginator, 'page_obj': children})
class ChildView(LoginRequiredMixin,View):
    login_url = settings.LOGIN_URL
    def get(self, request , *args, **kwargs):
        page = request.GET.get('page')
        child = Child.objects.filter(company = request.user.company, is_active=True).order_by('-id')
        group = Group.objects.filter(company = request.user.company, is_active=True)
        paginator = Paginator(child,2)  
        tarif = TarifCompany.objects.filter(company = request.user.company, is_active=True,status=2)
        try:
            children = paginator.page(page)
        except PageNotAnInteger:
            children = paginator.page(1)
        except EmptyPage:
            children = paginator.page(paginator.num_pages)
        return render (request ,'child.html', {'child':children,"group":group ,'tarif':tarif})
    
    def post(self,request):
        name = request.POST.get('name')
        phone = request.POST.get('phone')
        date = request.POST.get('date')
        group = request.POST.get('group')
        group = Group.objects.get(id=int(group))
        child = Child.objects.create(
            company = request.user.company,
            name=name,
            phone=phone,
            birth_date = date,
            group = group
        )
        messages.error(request, f"{child.name} Qo'shildi {group.name} ga")
        return redirect('/child')

@login_required
def chaild_edit(request,pk):
    child = Child.objects.get(id=pk)
    name = request.POST.get('name')
    phone = request.POST.get('phone')
    group = request.POST.get('group')
    child.name  = name
    child.phone  = phone
    child.group_id  = group
    child.save()
    messages.error(request, f"ozgarishlar amalga oshdi ")
    return redirect('child')

@login_required
def delete_chaild(request,pk):
    child = Child.objects.get(id=pk)
    child.is_active = False
    child.save()
    messages.error(request, f"{child.name} O'chirildi ")
    return redirect('child')


class TarifCompanyView(LoginRequiredMixin,View):
    login_url = settings.LOGIN_URL
    def get(self,request):
        tarif_company = TarifCompany.objects.filter(company = request.user.company,is_active = True)
        status = request.GET.get('status')
        if status:
            tarif_company = tarif_company.filter(status=status)
        status = TarifCompany.STATUS
        return render(request,'tarif.html',{'tarif':tarif_company,'status':status})
    def post (self,request):
        name = request.POST.get('name')
        status = request.POST.get('status')
        amount = request.POST.get('amount')
        TarifCompany.objects.create(
            company = request.user.company,
            name = name,
            status = status,
            amount = amount,
            created = timezone.now()
        )
        messages.error(request, f"Tarif Qo'shildi ")
        return redirect('tarif')
@login_required
def edit_tarif(request,pk):
    tarif = TarifCompany.objects.get(id=pk)
    name = request.POST.get('name')
    status = request.POST.get('status')
    amount = request.POST.get('amount')
    tarif.name = name
    tarif.status = status
    tarif.amount = amount
    tarif.created = timezone.now()
    tarif.save()
    messages.error(request, f"Tarif O'zgardi ")
    return redirect('tarif')

@login_required
def chaild_edit_tarif(request,pk):
    child = get_object_or_404(Child , id=pk)
    tarif = request.POST.get('tarif')
    tarif = get_object_or_404( TarifCompany , id=tarif)
    child.tarif = tarif
    child.save()
    messages.error(request, f"Tarif O'zgardi ")
    return redirect('child')

