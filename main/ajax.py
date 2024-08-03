
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from .models import *

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