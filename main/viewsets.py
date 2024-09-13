from rest_framework.response import Response
from rest_framework import viewsets
from .models import *
from .serializers import *

class CompanyViewSet(viewsets.ModelViewSet):
    def get_queryset(self):
        company_id = self.request.user.company_id
        queryset = Company.objects.filter(company_id=company_id)
        return queryset
    serializer_class = CompanySerializer
    def destroy(self, request, *args, **kwargs):
        queryset = self.get_object()
        queryset.is_active = False
        queryset.save()
        return  Response({'success':True})
    
    
class TeacherViewSet(viewsets.ModelViewSet):
    def get_queryset(self):
        company_id = self.request.user.company_id
        queryset = Teacher.objects.filter(company_id=company_id)
        return queryset
    serializer_class = TeacherSerializer
    def destroy(self, request, *args, **kwargs):
        queryset = self.get_object()
        queryset.is_active = False
        queryset.save()
        return  Response({'success':True})

class ChildViewSet(viewsets.ModelViewSet):
    def get_queryset(self):
        company_id = self.request.user.company_id
        queryset = Child.objects.filter(company_id=company_id)
        return queryset
    serializer_class = ChildSerializer
    def destroy(self, request, *args, **kwargs):
        queryset = self.get_object()
        queryset.is_active = False
        queryset.save()
        return  Response({'success':True})

class GroupViewSet(viewsets.ModelViewSet):
    def get_queryset(self):
        company_id = self.request.user.company_id
        queryset = Group.objects.filter(company_id=company_id)
        return queryset
    serializer_class = GroupSerializer
    def destroy(self, request, *args, **kwargs):
        queryset = self.get_object()
        queryset.is_active = False
        queryset.save()
        return  Response({'success':True})

class AttendanceViewSet(viewsets.ModelViewSet):
    def get_queryset(self):
        company_id = self.request.user.company_id
        queryset = Attendance.objects.filter(company_id=company_id)
        return queryset
    serializer_class = AttendanceSerializer
    def destroy(self, request, *args, **kwargs):
        queryset = self.get_object()
        queryset.is_active = False
        queryset.save()
        return  Response({'success':True})

class PaymentViewSet(viewsets.ModelViewSet):
    def get_queryset(self):
        company_id = self.request.user.company_id
        queryset = Payment.objects.filter(company_id=company_id)
        return queryset
    serializer_class = PaymentSerializer
    def destroy(self, request, *args, **kwargs):
        queryset = self.get_object()
        queryset.is_active = False
        queryset.save()
        return  Response({'success':True})

class TransferViewSet(viewsets.ModelViewSet):
    def get_queryset(self):
        company_id = self.request.user.company_id
        queryset = Transfer.objects.filter(company_id=company_id)
        return queryset
    serializer_class = TransferSerializer
    def destroy(self, request, *args, **kwargs):
        queryset = self.get_object()
        queryset.is_active = False
        queryset.save()
        return  Response({'success':True})

class ChashViewSet(viewsets.ModelViewSet):
    def get_queryset(self):
        company_id = self.request.user.company_id
        queryset = Cash.objects.filter(company_id=company_id)
        return queryset
    serializer_class = ChashSerializer
    def destroy(self, request, *args, **kwargs):
        queryset = self.get_object()
        queryset.is_active = False
        queryset.save()
        return  Response({'success':True})
