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
from django.db.models.functions import TruncMonth
from dateutil.relativedelta import relativedelta
from django.utils import translation


class HomeView(LoginRequiredMixin, View):
    login_url = settings.LOGIN_URL

    def get(self, request):
        language =  translation.get_language()
        if request.session.get('language','uz') != language :
            language = request.session.get('language','uz') 
            return redirect(f'/{language}/')
        today = timezone.now()
        last_12_months = [(today - relativedelta(months=i)).strftime("%Y-%m") for i in range(11, -1, -1)]

        # Kirim va chiqim uchun to'liq so'rovlar
        payments = Payment.objects.filter(
            company=request.user.company,
            date__gte=today - relativedelta(years=1)
        ).annotate(month=TruncMonth('date')).values('month', 'payment_type')\
            .annotate(total_amount=Sum('amount')).order_by('month')

        # Kirim va chiqimni to'plab olish
        revenue_dict = {item['month'].strftime("%Y-%m"): item['total_amount'] for item in payments if item['payment_type'] == 1}
        cost_dict = {item['month'].strftime("%Y-%m"): item['total_amount'] for item in payments if item['payment_type'] == 2}

        revenue_data = [float(revenue_dict.get(month, 0)) for month in last_12_months]
        cost_data = [float(cost_dict.get(month, 0)) for month in last_12_months]
        profit_data = [revenue - cost for revenue, cost in zip(revenue_data, cost_data)]
        
        context = {
            'apex_series': [
                {
                    "name": "Kirim",
                    "data": revenue_data,
                    "color": "#28a745"  # Yashil rang
                },
                {
                    "name": "Chiqim",
                    "data": cost_data,
                    "color": "#dc3545"  # Qizil rang
                },
                {
                    "name": "Foyda",
                    "data": profit_data,
                    "color": "#007bff"  # Ko'k rang
                }
            ],
            'last_12_months': last_12_months
        }
        return render(request, 'index.html', context)


class TeacherView(LoginRequiredMixin,View):
    login_url = settings.LOGIN_URL
    def get(self, request):
        company_id = request.user.company.id
        teacher = Teacher.objects.filter(company_id=company_id, is_active=True)\
                    .prefetch_related('group_teachers','group_teachers__teacher', 'group_helpers','group_helpers__helper')\
                        .select_related('company', 'tarif')
        
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
        other_groups = Group.objects.filter(company_id=company_id).exclude(pk__in=group).select_related('teacher','helper')
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
        main = request.POST.get('main')
        cahs = request.POST.get('cahs')
        user = get_object_or_404(Teacher, id=pk)
        user.username = username
        user.phone = phone
        user.type = type
        user.is_payment = payment == 'on' 
        user.is_salary = salary == 'on' 
        user.is_child = child  == 'on' 
        user.is_active = active == 'on'
        user.is_main = main == 'on'
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
        language = translation.get_language()
        return redirect (f'/{language}/teacher/{pk}/')


class GroupView(LoginRequiredMixin,View):
    login_url = settings.LOGIN_URL
    def get(self,request,*args, **kwargs):
        company = request.user.company 
        group =  Group.objects.filter(company=company, is_active = True)\
            .select_related('teacher', 'helper')
        return render(request,'group.html',{'group':group}) 
    
    def post(self,request, *args, **kwargs):
        name = request.POST.get('name')
        Group.objects.create(
            name=name,
            company=request.user.company,
        )
        language = translation.get_language()
        return redirect(f'/{language}/group')
    

class GroupDetailView(LoginRequiredMixin, View):
    login_url = settings.LOGIN_URL
    
    def get(self, request, pk, *args, **kwargs):
        today = request.GET.get('date')
        if not today:
            today = timezone.now().date()
        else:
           today = datetime.strptime(today,  '%d-%m-%Y').date()
        
        

        # start_time = time.time() 
        company = request.user.company  
        page = request.GET.get('page')
        group = Group.objects.get(id=pk)
        start_of_month = today.replace(day=1)

        children = Child.objects.filter(company=company, group=group,is_active = True).select_related('tarif').prefetch_related('payments')
        children_cout = children.count()
        # Attendance counts for today and this month
        attendance_counts = Attendance.objects.filter(
            company=company, 
            child__in=children,
            date__gte=start_of_month,
            is_active = True
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

            attendance_today = today_count == 1

            payment_summa_value = payment_summa_dict.get(child.id, 0)
            tarif_amount = child.tarif.amount if child.tarif else 0
            remaining_amount = tarif_amount - payment_summa_value
            children_attendance.append({
                'child': child,
                'attendance_today': attendance_today,
                'attendance_monthly': monthly_count,
                'payment_summa': payment_summa_value,
                'remaining_amount': remaining_amount
            })

        context = {
            'group': group,
            'paginator': paginator,
            'children_cout':children_cout,
            'page_obj': paginated_children,
            'children_attendance': children_attendance,
            'date':today
        }

        # end_time = time.time() 
        # duration = end_time - start_time  # So'rovning bajarilish vaqti
        return render(request, 'group-detail.html', context)


class ChildView(LoginRequiredMixin,View):
    login_url = settings.LOGIN_URL
    def get(self, request , *args, **kwargs):
        page = request.GET.get('page')
        company = request.user.company

        child = (
            Child.objects
            .filter(company=company, is_active=True)
            .select_related('group', 'company', 'tarif')
            .order_by('-id')
        )
        
        group = (
            Group.objects
            .filter(company=company, is_active=True)
            .select_related('company', 'teacher', 'helper')
            .order_by('-id')
        )
        
        tarif = (
            TarifCompany.objects
            .filter(company=company, is_active=True, status=2)
            .select_related('company')
        )
        
        paginator = Paginator(child,20)  
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
        language = translation.get_language()
        return redirect(f'/{language}/child')


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
        language = translation.get_language()
        return redirect(f'/{language}/tarif')


class PaymentView(LoginRequiredMixin,View):
    login_url = settings.LOGIN_URL
    def get(self, request):

        page = request.GET.get('page')

        payments = Payment.objects.filter(company=request.user.company, payment_type=1)\
            .select_related('child','teacher','user').order_by('-id')
        paginator = Paginator(payments, 25)  # Sahifalarni 25 tadan ko'rsatish
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
        year = int(datetime.now().year)
        page = request.GET.get('page')
        category = PaymentCategory.objects.filter(company=request.user.company,)
        payments = Payment.objects.filter(company=request.user.company, payment_type=2)\
            .select_related('child','teacher','user').order_by('-id')
            
        total_amount = Payment.objects.filter(payment_type=2,
                date__gte=date.today().replace(day=1),
                is_active=True
            ).select_related('child','teacher','user')\
            .aggregate(total_amount=Sum('amount'))['total_amount'] or 0

        print(total_amount)
        paginator = Paginator(payments, 25) 
   
        try:
            payment_page = paginator.page(page)
        except PageNotAnInteger:
            payment_page = paginator.page(1)
        except EmptyPage:
            payment_page = paginator.page(paginator.num_pages)

        
        
        context = {
            'payment': payment_page,
            'category':category,
            'total_amount' :total_amount,
            'year':year
    
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
    def post(self,request):
        id = request.POST.get('id')
        amount = Decimal(request.POST.get('amount'))
        cahs = get_object_or_404(Cash,id=id)
        cahs.amount = amount
        cahs.save()
        messages.error(request, f"Kassa yangilandi")
        language = translation.get_language()
        return  redirect(f'/{language}/cash/')
        

class TransferView(LoginRequiredMixin,View):
    login_url = settings.LOGIN_URL
    def get(self,request, *args, **kwargs):
        page = request.GET.get('page')
        transfer = Transfer.objects.filter(company=request.user.company).order_by('-id')\
            .select_related('user','teacher_1', 'teacher_2')
        teachar = Teacher.objects.filter(company=request.user.company, cash__is_active = True)\
            .select_related('tarif','company')
        paginator = Paginator(transfer, 25)  # Sahifalarni 25 tadan ko'rsatish
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


class SettingsView(LoginRequiredMixin,View):
    def get(self, request,):
        tarif = Tarif.objects.all()
        category = PaymentCategory.objects.filter(company=request.user.company)
        working_day = [ i for i in range(1,32) ]
        context = {
            'working_day':working_day,
            'tarif':tarif,
            'category':category
        }
        return render (request, 'settings.html', context)
    
    def post(self,request,):
        id = request.POST.get('tarif')
        company =  request.user.company 
        tarif  = Tarif.objects.get(id=id)
        company.tarif = tarif
        company.save()
        messages.error(request,'tarif almashdi ')
        language = translation.get_language()
        return redirect(f'/{language}/settings')


@login_required
def working_day(request):
    working_day = request.POST.get('working_day')
    company =  request.user.company 
    company.working_day = int(working_day)
    company.save()
    messages.error(request,' ish kuni almashdi  ')
    language = translation.get_language()
    return redirect(f'/{language}/settings')


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
    language = translation.get_language()
    return redirect(f'/{language}/tarif')


@login_required
def chaild_edit_tarif(request,pk):
    child = get_object_or_404(Child , id=pk)
    tarif = request.POST.get('tarif')
    tarif = get_object_or_404( TarifCompany , id=tarif)
    child.tarif = tarif
    child.save()
    messages.error(request,"Tarif Ozgardi ")
    language = translation.get_language()
    return redirect(f'/{language}/child')


@login_required
def calendar_child(request,pk):
    child = Child.objects.get(id=pk)
    today = datetime.today()
    six_months_ago = today - relativedelta(months=6)
    first_day_of_six_months_ago = six_months_ago.replace(day=1)
    attendance = Attendance.objects.filter(
        child=child,
        is_active=True,
        date__range=[first_day_of_six_months_ago, today]
    ).values('id', 'child__name', 'date')

 
    events = [
        {
            'id': record['id'],
            'title': f'Keldi {record["child__name"]}',  
            'start': record['date'].strftime('%Y-%m-%dT%H:%M:%S'), 
            'allDay': True,
            'className': 'info',
            
        }
        for record in attendance
    ]
    

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
    ).values('id', 'teacher__username', 'date')


    events = [
            {
            'id': record['id'],
            'title': f"Keldi {record['teacher__username']}",  
            'start': record['date'].strftime('%Y-%m-%dT%H:%M:%S'), 
            'allDay': True,
            'className': 'info',
            }
            for record in attendance
        ]
    events_json = json.dumps(events)
    
    return render(request, 'fullcalendar.html', {'events_json': events_json})


@login_required
def payment_child(request, pk):
    child =  get_object_or_404( Child , id=pk)
    summa = request.POST.get('summa')
    date_month= request.POST.get('date_month')  
    description = request.POST.get('description', None)
    cash = request.user.cash
    language = translation.get_language()
    if cash.is_active :
        payment = Payment.objects.create(
            company = request.user.company,  
            user=request.user,
            child = child,
            amount = summa,
            payment_type = 1,
            date_month = date_month,
            description = description ,
            user_before_cash = cash.amount,
            
        )
        cash = Cash.objects.get(teacher=request.user)
        cash.amount += Decimal(payment.amount)
        cash.save()
        payment.user_after_cash = cash.amount
        payment.save()
        messages.error(request, f"{child.name} Tplov Qildi ")
        return redirect(f'/{language}/group-detail/{child.group.id}/')
    messages.error(request, 'sizda shahsi kassa yoqilmagan  ')
    return redirect(f'/{language}/group-detail/{child.group.id}/')


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
    language = translation.get_language()
    return redirect(f'/{language}/child')


@login_required
def delete_chaild(request,pk):
    child = Child.objects.get(id=pk)
    child.is_active = False
    child.save()
    messages.error(request, f"{child.name} Ochirildi ")
    language = translation.get_language()
    return redirect(f'/{language}/child')


@login_required
def password(request,pk):
        password = request.POST.get('password')
        user = get_object_or_404(Teacher, id=pk)
        user.set_password(password)
        user.save()
        language = translation.get_language()

        return redirect (f'/{language}/teacher/{pk}/')


@login_required
def salary(request, pk):
    user = get_object_or_404(Teacher, id=pk)
    tarif =request.POST.get('tarif')
    tarif = get_object_or_404(TarifCompany, id=tarif)
    user.tarif = tarif
    user.save()
    messages.error(request, 'tarif almashdi ')
    language = translation.get_language()
    return redirect(f'/{language}/teacher/{pk}/')
        

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
    language = translation.get_language()
    return redirect (f'/{language}/teacher')


@login_required
def create_payment_category(request):
    name = request.POST.get('category')
    PaymentCategory.objects.get_or_create(
        name =name,
        company = request.user.company
    )
    messages.error(request, 'Category qoshildi')
    language = translation.get_language()
    return redirect(f'/{language}/settings/')

def edit_cpayment_catedory_deleteategory (request, pk):
    PaymentCategory.objects.get(id=int(pk)).delete()
    messages.error(request, 'Category ochrildi')
    language = translation.get_language()
    return redirect(f'/{language}/settings/')