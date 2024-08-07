
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from .models import *
from decimal import Decimal
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
        print(teacer_id)
        is_active = request.POST.get('is_active') == 'true'
        date = timezone.now().date()
        attendance, created = Attendance.objects.update_or_create(
            company = company,  
            teacher_id=teacer_id,
            date=date,
            defaults={ 'is_active': is_active},
        )
        return JsonResponse({'status': 'success', 'attendance_id': attendance.id})

class UpdateAttendancePaymenntView(View):
    @method_decorator(require_POST)
    def post(self, request, *args, **kwargs):
        payment_id = request.POST.get('payment_id')
        amount = request.POST.get('amount')
        date_month = request.POST.get('date_month')
        description = request.POST.get('description')

        try:
            payment = Payment.objects.get(id=payment_id, company=request.user.company)
            cash = payment.user.cash_teachers.all().last()
            if not payment.is_edit : 
                cash.amount -= payment.amount 
                cash.amount += Decimal( amount)
                payment.amount = Decimal (amount)
                payment.date_month = date_month
                payment.description = description
                payment.save()
                cash.save()

            return JsonResponse({
                'status': 'success',
                'payment_id': payment.id,
                'amount': payment.amount,
                'date_month': payment.date_month,
                'description': payment.description
            })
        except Payment.DoesNotExist:
            return JsonResponse({'status': 'fail', 'message': 'Payment not found'}, status=404)
        except Exception as e:
            return JsonResponse({'status': 'fail', 'message': str(e)}, status=400)