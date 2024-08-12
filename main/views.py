from django.shortcuts import render , redirect ,get_object_or_404
from django.conf import settings
from django.views import View
from .models import *
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from decimal import Decimal
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage 
from django.db.models import Count
import json
from datetime import datetime, timedelta
import time
from django.db.models import Sum, Q, Value , OuterRef, Subquery
from django.db.models.functions import Coalesce
from django.conf import settings

class HomeView(LoginRequiredMixin,View):
    login_url = settings.LOGIN_URL
    def get(self, request):

        return render(request, 'index.html')


class TeacherView(LoginRequiredMixin,View):
    login_url = settings.LOGIN_URL
    def get(self, request):
        company_id = request.user.company.id
        teacher = Teacher.objects.filter(company_id=company_id, is_active=True)\
                    .prefetch_related('group_teachers', 'group_helpers')
        
        today = timezone.now().date()
        attendances = Attendance.objects.filter(teacher__in=teacher, date=today)
        attendance_dict = {att.teacher_id: att for att in attendances}
        teacher_attendance = []
        for t in teacher:
            attendance = attendance_dict.get(t.id, None)
            teacher_attendance.append({
                'teacher': t,
                'attendance': attendance,
            })
        context = {
            'teacher': teacher,
            'type': Teacher.TYPE,
            'teacher_attendance': teacher_attendance
        }
        return render(request, 'teacher-all.html', context)

     


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
        cahs = request.POST.get('cahs')
        user = get_object_or_404(Teacher, id=pk)
        user.username = username
        user.phone = phone
        user.type = type
        user.is_payment = payment == 'on' 
        user.is_salary = salary == 'on' 
        user.is_child = child  == 'on' 
        user.is_active = active == 'on'
        user.cash.is_active = cahs == 'on'
        user.cash.save()
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
        teacher = Teacher.objects.create_user(
        company = company,
        username=request.POST.get('username'),
        phone=request.POST.get('phone'),
        password=request.POST.get('password'),
        type = request.POST.get('type')
        )
        Cash.objects.get_or_create(
                company=company,
                teacher=teacher,
                is_active = False
            )
        messages.error(request, f"{teacher.username} Qoshildi ")
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

   
        # start_time = time.time() 

        company = request.user.company
        page = request.GET.get('page')
        group = Group.objects.get(id=pk)
        today = timezone.now().date()
        start_of_month = today.replace(day=1)

        children = Child.objects.filter(company=company, group=group).select_related('tarif').prefetch_related('payments')

        # Attendance counts for today and this month
        attendance_counts = Attendance.objects.filter(
            company=company, 
            child__in=children,
            date__gte=start_of_month,
            presence=True
        ).values('child_id').annotate(
            today_count=Count('id', filter=Q(date=today)),
            monthly_count=Count('id')
        )

        attendance_dict_count = {att['child_id']: (att['today_count'], att['monthly_count']) for att in attendance_counts}

        # Payment summary
        payment_summa = Payment.objects.filter(
            company=company, 
            child__in=children,
            date_month__gte=start_of_month
        ).values('child_id').annotate(
            amount=Sum('amount')
        )

        payment_summa_dict = {pay['child_id']: pay['amount'] for pay in payment_summa}

        # Paginate children
        paginator = Paginator(children, 25)
        try:
            paginated_children = paginator.page(page)
        except PageNotAnInteger:
            paginated_children = paginator.page(1)
        except EmptyPage:
            paginated_children = paginator.page(paginator.num_pages)

        # Combine all data for children
        children_attendance = []
        for child in paginated_children:
            today_count, monthly_count = attendance_dict_count.get(child.id, (0, 0))
            payment_summa_value = payment_summa_dict.get(child.id, 0)
            tarif_amount = child.tarif.amount if child.tarif else 0
            remaining_amount = tarif_amount - payment_summa_value
            children_attendance.append({
                'child': child,
                'attendance_today': today_count,
                'attendance_monthly': monthly_count,
                'payment_summa': payment_summa_value,
                'remaining_amount': remaining_amount
            })

        context = {
            'group': group,
            'page_obj': paginated_children,
            'paginator': paginator,
            'children_attendance': children_attendance,
        }

        # end_time = time.time() 
        # duration = end_time - start_time  # So'rovning bajarilish vaqti



        return render(request, 'group-detail.html', context)


class ChildView(LoginRequiredMixin,View):
    login_url = settings.LOGIN_URL
    def get(self, request , *args, **kwargs):
        page = request.GET.get('page')
        child = Child.objects.filter(company = request.user.company, is_active=True).order_by('-id')
        group = Group.objects.filter(company = request.user.company, is_active=True)
        paginator = Paginator(child,10)  
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
        messages.error(request, f"{child.name} Qoshildi {group.name} ga")
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
    messages.error(request, f"{child.name} Ochirildi ")
    return redirect('child')


class TarifCompanyView(LoginRequiredMixin,View):
    login_url = settings.LOGIN_URL
    def get(self,request):
       
        tarif_company = TarifCompany.objects.filter(
            company = request.user.company,
            is_active = True,
             )
        
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
        messages.error(request, f"Tarif Qoshildi ")
        return redirect('tarif')
@login_required
def edit_tarif(request,pk):
    tarif = TarifCompany.objects.get(id=pk)
    name = request.POST.get('name')
    status = request.POST.get('status')
    amount = request.POST.get('amount')
    tarif.name = name
    tarif.status = int(status)
    tarif.amount = amount
    tarif.created = timezone.now()
    tarif.save()
    messages.error(request, f"Tarif Ozgardi ")
    return redirect('tarif')

@login_required
def chaild_edit_tarif(request,pk):
    child = get_object_or_404(Child , id=pk)
    tarif = request.POST.get('tarif')
    tarif = get_object_or_404( TarifCompany , id=tarif)
    child.tarif = tarif
    child.save()
    messages.error(request,"Tarif Ozgardi ")
    return redirect('child')

@login_required
def calendar_child(request,pk):
    child = Child.objects.get(id=pk)
    today = datetime.today()
    first_day_of_current_month = today.replace(day=1)
    first_day_of_previous_month = (first_day_of_current_month - timedelta(days=1)).replace(day=1)
    attendance = Attendance.objects.filter(
        child=child,
        is_active=True,
        date__range=[first_day_of_previous_month, today]
    )
    
    events = []
    for record in attendance:
        events.append({
            'id': record.id,
            'title': f'Keldi  {record.child.name}',  
            'start': record.date.strftime('%Y-%m-%dT%H:%M:%S'), 
            'allDay': True,
            'className': 'info',
            })
    events_json = json.dumps(events)
    
    return render(request, 'fullcalendar.html', {'events_json': events_json})

@login_required
def calendar_teacher(request,pk):
    teacher = Teacher.objects.get(id=pk)
    
    today = datetime.today()
    first_day_of_current_month = today.replace(day=1)
  
    first_day_of_previous_month = (first_day_of_current_month - timedelta(days=1)).replace(day=1)

    attendance = Attendance.objects.filter(
        teacher=teacher,
        is_active=True,
        date__range=[first_day_of_previous_month, today]
    )
    
    events = []
    for record in attendance:
        events.append({
            'id': record.id,
            'title': f'Keldi  {record.teacher}',  
            'start': record.date.strftime('%Y-%m-%dT%H:%M:%S'), 
            'allDay': True,
            'className': 'info',
            })
    events_json = json.dumps(events)
    
    return render(request, 'fullcalendar.html', {'events_json': events_json})

@login_required
def payment_child(request, pk):
    child =  get_object_or_404( Child , id=pk)
    summa = request.POST.get('summa') 
    date_month= request.POST.get('date_month')  
    description = request.POST.get('description', None)
    cash = request.user.cash
    if cash.is_active :
        payment = Payment.objects.create(
            company = request.user.company,  
            user=request.user,
            child = child,
            amount = summa,
            payment_type = 1,
            date_month = date_month,
            description = description ,
            
        )
        cash = Cash.objects.get(teacher=request.user)
        cash.amount += Decimal(payment.amount)
        cash.save()
        payment.save()
        messages.error(request, f"{child.name} Tplov Qildi ")
    messages.error(request, ' sizda shahsi kassa yoqilmagan  ')
    return redirect(f'/group-detail/{child.group.id}/')


class PaymentView(LoginRequiredMixin,View):
    login_url = settings.LOGIN_URL
    def get(self, request):

        page = request.GET.get('page')

        payments = Payment.objects.filter(company=request.user.company, payment_type=1)\
            .select_related('child','teacher','user').order_by('-id')
        paginator = Paginator(payments, 10)  # Sahifalarni 25 tadan ko'rsatish
        try:
            payment_page = paginator.page(page)
        except PageNotAnInteger:
            payment_page = paginator.page(1)
        except EmptyPage:
            payment_page = paginator.page(paginator.num_pages)

        context = {
            'payment': payment_page,
          
        }
        return render(request, 'payment.html', context)


class PaymentCostView(LoginRequiredMixin,View):
    login_url = settings.LOGIN_URL
    def get(self, request):
        page = request.GET.get('page')
        
        payments = Payment.objects.filter(company=request.user.company, payment_type=2)\
            .select_related('child','teacher','user').order_by('-id')
        paginator = Paginator(payments, 2)  # Sahifalarni 25 tadan ko'rsatish
        try:
            payment_page = paginator.page(page)
        except PageNotAnInteger:
            payment_page = paginator.page(1)
        except EmptyPage:
            payment_page = paginator.page(paginator.num_pages)

        context = {
            'payment': payment_page,
    
        }
        return render(request, 'payment.cost.html', context)


class CashView(LoginRequiredMixin,View):
    login_url = settings.LOGIN_URL
    def get(self,request,):
        company = request.user.company 
        
        month = int(request.GET.get('month', datetime.now().month))
        year = int(request.GET.get('year', datetime.now().year))

        start_date = datetime(year, month, 1)
        next_month = start_date.replace(day=28) + timedelta(days=4)  # Keyingi oyning birinchi kuni
        end_date = next_month - timedelta(days=next_month.day)  # Tanlangan oyning oxirgi kuni

        cash = Cash.objects.filter(company=company, is_active=True).annotate(
            total_kirim=Coalesce(
                Sum(
                    'teacher__payments_user__amount',
                    filter=Q(teacher__payments_user__date__range=(start_date, end_date)) &
                           Q(teacher__payments_user__payment_type=1),
                    output_field=DecimalField()
                ),
                Value(1),
                output_field=DecimalField()
            ),
            total_chiqim=Coalesce(
                Sum(
                    'teacher__payments_user__amount',
                    filter=Q(teacher__payments_user__date__range=(start_date, end_date)) &
                           Q(teacher__payments_user__payment_type=2),
                    output_field=DecimalField()
                ),
                Value(1),
                output_field=DecimalField()
            ),
        ).order_by('-total_kirim', '-total_chiqim').select_related('teacher')
        
        number_list = [ i for i in range(1,13)] 
        context = {
            'cash': cash,
            'selected_month': month,
            'selected_year': year,
            'number_list':number_list
        } 
        return render (request, 'cash.html', context)

class TransferView(LoginRequiredMixin,View):
    login_url = settings.LOGIN_URL
    def get(self,request, *args, **kwargs):
        page = request.GET.get('page')
        transfer = Transfer.objects.filter(company=request.user.company).order_by('-id')
        teachar = Teacher.objects.filter(company=request.user.company, cash__is_active = True)
        paginator = Paginator(transfer, 10)  # Sahifalarni 25 tadan ko'rsatish
        try:
            transfer = paginator.page(page)
        except PageNotAnInteger:
            transfer = paginator.page(1)
        except EmptyPage:
            transfer = paginator.page(paginator.num_pages)
        context = {
            'transfer':transfer,
            'teachar':teachar
            }
        return render(request, 'transfer.html',context)