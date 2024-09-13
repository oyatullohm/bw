from django.db.models import Q, F, Sum, Case, When, Prefetch, FloatField, DecimalField
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from rest_framework import viewsets, pagination
from rest_framework.decorators import action
from rest_framework.response import Response
from decimal import Decimal
from main.models import *
from .serializer import *


class GroupViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class  = GroupSerializer
    def get_queryset(self):
        company = self.request.user.company
        queryset = Group.objects.filter(company=company)
        return queryset
    
    def create(self, request, *args, **kwargs):
        data = request.data
        group =  Group.objects.create(company = request.user.company,name=data['name'])
        return Response({
            "success":True,
            'data':GroupSerializer(group, many=False).data
        })

    @action(methods=['get'], detail=True)
    def group_detail(self, request, *args, **kwargs):
        group_id = kwargs['pk']
        child = Child.objects.filter(group__id=group_id).select_related('company', 'tarif', 'group')
        serializer = ChildSerializer(child, many= True)
        return Response({
            "success": True,
            'data': serializer.data
        })      


class TeacherViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class  = UserSerializer
    def get_queryset(self):
        company = self.request.user.company
        queryset = Teacher.objects.filter(company=company)
        return queryset
    
    def create(self, request, *args, **kwargs):
        data = request.data
        teacher = Teacher.objects.create_user(
            company= request.user.company,
            username=data['username'],
            password=data['password'],
            phone=data['phone'],
            type = data['type']
        )
        return Response({
            "success":True,
            'data':UserSerializer(teacher, many=False).data
        })

    def update(self, request, *args, **kwargs):
        data = request.data
        if request.user.is_main:
            teacher = Teacher.objects.get(id=kwargs['pk']) 
            teacher.username = data['username']
            teacher.type = data['type']
            teacher.phone = data['phone']
            teacher.is_payment = data['is_payment']
            teacher.is_main = data['is_main']
            teacher.is_child = data['is_child']
            teacher.is_salary = data['is_cash']
            teacher.save()

            return Response({
                "success":True,
                'data':UserSerializer(teacher, many=False).data
            })
        return Response({
                "success":False,
                "messages":"Permission None"
               
            })
class PaymentViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = PaymentSerializer
    def get_queryset(self):
        company = self.request.user.company
        queryset = Payment.objects.filter(company=company)
        return queryset
    def create(self, request, *args, **kwargs):
        data = request.data
        child = None
        if data.get('child'):
            child =  Child.objects.get(id=data.get('child'))
        summa = data.get('summa')
        date_month= data.get('date_month')  
        description = data.get('description', None)
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
                user_before_cash = cash.amount,
                
            )
            cash = Cash.objects.get(teacher=request.user)
            cash.amount += Decimal(payment.amount)
            cash.save()
            payment.user_after_cash = cash.amount
            payment.save()
        return Response({
                "success":False, 
            })