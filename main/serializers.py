from rest_framework import serializers
from .models import*

class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = '__all__'

class TeacherSerializer(serializers.ModelSerializer):
    class Meta:
        model = Teacher
        fields = '__all__'

class ChildSerializer(serializers.ModelSerializer):
    class Meta:
        model = Child
        fields = '__all__'

class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = '__all__'



class AttendanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attendance
        fields = '__all__'

class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = '__all__'

class TransferSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transfer
        fields = '__all__'

class ChashSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cash
        fields = '__all__'
