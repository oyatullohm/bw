from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework import viewsets, pagination
from django.db.models import Q, Sum, Case, When, DecimalField , F ,Prefetch , FloatField
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