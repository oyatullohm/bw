
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from .models import *
from decimal import Decimal
from django.contrib import messages
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
import json


@method_decorator(csrf_exempt, name='dispatch')
class UpdateAttendanceChildView(View):
    @method_decorator(require_POST)
    def post(self, request, *args, **kwargs):
        company = request.user.company
        child_id = request.POST.get('child_id')
        is_active = request.POST.get('is_active') == 'true'
        date = timezone.now().date()
        attendance, created = Attendance.objects.update_or_create(
            company = company,  
            child_id=child_id,
            date=date,
            defaults={ 'is_active': is_active},
        )
        return JsonResponse({'status': 'success', 'attendance_id': attendance.id})


@method_decorator(csrf_exempt, name='dispatch')
class UpdateAttendanceTeacherView(View):
    @method_decorator(require_POST)
    def post(self, request, *args, **kwargs):
        company = request.user.company
        teacer_id = request.POST.get('teacer_id')
        is_active = request.POST.get('is_active') == 'true'
        date = timezone.now().date()
        attendance, created = Attendance.objects.update_or_create(
            company = company,  
            teacher_id=teacer_id,
            date=date,
            defaults={ 'is_active': is_active},
        )
        return JsonResponse({'status': 'success', 'attendance_id': attendance.id})


@method_decorator(csrf_exempt, name='dispatch')
class UpdatePaymenntView(View):
    @method_decorator(require_POST)
    def post(self, request, *args, **kwargs):
        payment_id = request.POST.get('payment_id')
        amount = request.POST.get('amount')
        date_month = request.POST.get('date_month')
        description = request.POST.get('description')

        try:
            amount = Decimal(amount)
            payment = Payment.objects.get(id=payment_id, company=request.user.company)
            cash = payment.user.cash
            if  payment.is_edit and timezone.now().date()-timedelta(days=3) < payment.date:
                if payment.payment_type == 1  :
                    payment.user_before_cash = cash.amount
                    cash.amount -= payment.amount
                    cash.amount += amount
                    payment.amount = amount
                    payment.date_month = date_month
                    payment.description = description
                    cash.save()
                    payment.user_after_cash = cash.amount 
                    payment.save()
                elif payment.payment_type == 2:

                    payment.user_before_cash = cash.amount
                    cash.amount += payment.amount
                    cash.amount -= amount
                    payment.amount = amount
                    payment.date_month = date_month
                    payment.description = description
                    cash.save()
                    payment.user_after_cash = cash.amount 
                    payment.save()
            else:
                messages.success(request, f"Tahrirlash muddati otgan")
            return JsonResponse({
                    'status': 'success',
                    'payment_id': payment.id,
                    'user':payment.user.username,
                    'amount': payment.amount,
                    'date_month': payment.date_month,
                    'date':payment.date,
                    'description': payment.description
                })
        except Payment.DoesNotExist:
            return JsonResponse({'status': 'fail', 'message': 'Payment not found'}, status=404)
        except Exception as e:
            return JsonResponse({'status': 'fail', 'message': str(e)}, status=400)


@method_decorator(csrf_exempt, name='dispatch')
class PaymentCreateView(View):
    @method_decorator(require_POST)
    def post(self, request, *args, **kwargs):
        amount = request.POST.get('amount')
        payment_type = request.POST.get('paymentType')
        description = request.POST.get('description')
        category = request.POST.get('category' , None)

        try:
            cash = request.user.cash

            if cash.is_active :
                payment =  Payment.objects.create(
                    company=request.user.company,
                    category_id = category,
                    user = request.user,
                    amount = Decimal(amount),
                    date_month=timezone.now(),
                    payment_type = int(payment_type),
                    description = description,
                    user_before_cash = cash.amount,
                    
                )

                if payment.payment_type == 1:
                    cash.amount += payment.amount
                elif payment.payment_type == 2:
                    cash.amount -= payment.amount
                payment.user_after_cash = cash.amount
                cash.save()
                payment.save()

                category_name = payment.category.name if payment.category else 'Category'

                return JsonResponse({
                    'status': 'success',
                    'date':payment.date,
                    'user':payment.user.username,
                    'amount': payment.amount,
                    'description': payment.description,
                    'category':category_name
                })
                
            messages.error(request, ' sizda shahsi kassa yoqilmagan  ')
            return JsonResponse({'status': 'success',})
        except Payment.DoesNotExist:
            return JsonResponse({'status': 'fail', 'message': 'Payment not found'}, status=404)
        except Exception as e:
            return JsonResponse({'status': 'fail', 'message': str(e)}, status=400)


@method_decorator(csrf_exempt, name='dispatch')
class TransferCreateView(View):
    @method_decorator(require_POST)
    def post(self, request, *args, **kwargs):
        amount = request.POST.get('amount')
        teacher_1 = request.POST.get('teacher_1')
        teacher_2 = request.POST.get('teacher_2')
        description = request.POST.get('description')
        teacher_1 = get_object_or_404(Teacher, id = teacher_1)
        teacher_2 = get_object_or_404(Teacher, id = teacher_2)
        if teacher_1 == teacher_2:
            return JsonResponse({'status': False})
            
        if teacher_1.cash.amount >= Decimal(amount):
            transfer = Transfer.objects.create(
                company = request.user.company,
                user=request.user,
                teacher_1 = teacher_1,
                teacher_2 = teacher_2,
                summa = Decimal(amount),
                description = description
            )
            
            transfer.teacher_1_before_cash = teacher_1.cash.amount
            transfer.teacher_2_before_cash = teacher_2.cash.amount
            

            teacher_1.cash.amount -= transfer.summa 
            teacher_1.cash.save()
            teacher_2.cash.amount += transfer.summa 
            teacher_2.cash.save()

            transfer.teacher_1_after_cash = teacher_1.cash.amount
            transfer.teacher_2_after_cash = teacher_2.cash.amount
            transfer.save()
            payment = Payment.objects.filter(company=request.user.company,
                                             user = teacher_1, is_edit = True).update(is_edit=False)
        return JsonResponse({'status': 'success'})


def search_payment_cost(request):
    query = request.GET.get('query', '')

    if query:
        conditions = Q(description__icontains=query)\
                    | Q(user__username__icontains=query)\
                    | Q(amount__icontains=query)\
                    | Q(category__name__icontains=query)
        results = Payment.objects.filter(
            conditions,
            company=request.user.company,
            payment_type=2
        ).select_related('user', 'category').order_by('-id')\
            .only( 'id','description', 'user__username',
                                      'amount','date','date_month','user_before_cash', 'user_after_cash')
        results = list(results.values('id','description', 'user__username', 
                                      'amount','date','date_month','user_before_cash', 'user_after_cash'))  # Natijalarni JSONga moslashtirish
    return JsonResponse(results, safe=False)


def search_payment(request):
    query = request.GET.get('query', '')

    if query:
        conditions =Q(child__name__icontains=query)\
                    |Q(user__username__icontains=query)\
                    |Q(amount__icontains=query)\
                    |Q(description__icontains=query)

        try:

            query_decimal = Decimal(query)
            conditions |= Q(amount=query_decimal)
        except :
            pass
        results = Payment.objects.filter(conditions, company=request.user.company, payment_type=1)\
        .select_related('user').order_by('-id')\
            .only( 'id','child__name','description', 'user__username', 
                                     'amount','date','date_month','user_before_cash', 'user_after_cash')
        results = list(results.values('id','child__name','description', 'user__username', 'category__name',
                                      'amount','date','date_month' ,'user_before_cash', 'user_after_cash'))  
        return JsonResponse(results, safe=False)
    return JsonResponse({'status':'success'})


def search_transfer(request):
    query = request.GET.get('query', '')

    if query:
        conditions =   Q(user__username__icontains=query)\
                    |  Q(description__icontains=query)\
                    |  Q(teacher_1__username__icontains=query)\
                    |  Q(teacher_2__username__icontains=query)
        try: 
            query_decimal = Decimal(query)
            conditions |= Q(summa=query_decimal)
        except :
            pass
        results = Transfer.objects.filter(conditions, company=request.user.company).order_by('-id')\
        .select_related('user').only('description',  'user__username',
                                     'teacher_1__username','teacher_2__username', 'summa',  'date',
                                     'teacher_1_before_cash','teacher_1_after_cash',
                                     'teacher_2_before_cash','teacher_2_after_cash')
        results = list(results.values('description',  'user__username',
                                     'teacher_1__username','teacher_2__username', 'summa',  'date',
                                     'teacher_1_before_cash','teacher_1_after_cash',
                                     'teacher_2_before_cash','teacher_2_after_cash')) 
        return JsonResponse(results, safe=False)
    return JsonResponse({'status':'success'})


def search_child(request):
    query = request.GET.get('query', '')

    if query:
        conditions=  Q(name__icontains=query)\
                    |Q(phone__icontains=query)\
                    |Q(group__name__icontains=query)
                            
                   
                
        results = Child.objects.filter(conditions, company=request.user.company,is_active=True)\
        .select_related('group').only( 'id', 'name',  'tarif__name','birth_date','phone','group__name')
        results = list(results.values('id', 'name',  'tarif__name','birth_date','phone','group__name')) 
        return JsonResponse(results, safe=False)
    return JsonResponse({'status':'success'})


@login_required    
def get_teacher_cash(request):
    teacher_id = request.GET.get('teacher_id')
    teacher = get_object_or_404(Teacher, id=teacher_id)
    cash = teacher.cash.amount  # teacherning cash summa qiymatini olamiz
    return JsonResponse({'cash': cash})


@csrf_exempt
def get_payments(request):
    if request.method == 'GET':
        category_id = int(request.GET.get('category_id') ) # GET parametridan category_id ni olish
        month = request.GET.get('month')  # GET parametridan category_id ni olish
        year = request.GET.get('year')

        if not month:
            month = datetime.today().strftime('%m')  # Hozirgi oy

        start_date = datetime(year=int(year), month=int(month), day=1).date()
        end_date = (start_date.replace(day=28) + timedelta(days=4)).replace(day=1) - timedelta(days=1)

        if category_id > 0 :
            payments = Payment.objects.filter(
                category_id=category_id,is_active=True,
                date__range=[start_date, end_date],
                payment_type = 2)
        else :
            payments = Payment.objects.filter(is_active=True ,
                                              date__range=[start_date, end_date], 
                                              payment_type=2)

        total_amount =payments.aggregate(total_amount=Sum('amount'))['total_amount'] or 0

        payment_data = [{
            'id': payment.id,
            'date': payment.date,
            'category':payment.category.name,
            'amount': payment.amount, 
            'user':payment.user.username,
            'description':payment.description,
            'user_before_cash':payment.user_before_cash,
            'user_after_cash':payment.user_after_cash,
        } for payment in payments]
        
        response_data ={
                'payment':payment_data,
                'total_amount':total_amount
                
             }
        return JsonResponse(response_data, safe=False)
    
    return JsonResponse({'error': 'Invalid request method'}, status=400)


@login_required
@csrf_exempt
def edit_category(request, category_id):
    category = get_object_or_404(PaymentCategory, id=category_id)
    print(category)
    category.name = request.POST.get('name')
    category.save()
    return JsonResponse({'success': True, 'new_name': category.name})
