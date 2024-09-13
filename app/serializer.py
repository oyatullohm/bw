
from main.models import *
from rest_framework import serializers


class TeacherSerializer(serializers.ModelSerializer):
    total_summa_master = serializers.ReadOnlyField()
    # total_points = TotalPointsSerializer(many=True, read_only=True, source='staffs')

    class Meta:
        model = Teacher
        fields = "__all__"

        extra_kwargs = {'password': {'write_only': True}}

      
class UserSerializer(serializers.ModelSerializer):
    company = serializers.CharField()
    type_display = serializers.SerializerMethodField()
    class Meta:
        model = Teacher
        fields = ['company', 'id', 'username', 'type_display', 'is_payment', 'is_salary', 'is_main', 'is_child']
    def get_type_display(self, obj):
        return obj.get_type_display()


class TarifSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tarif
        fields = ['id', 'name', 'summa', 'child', 'user', 'group']


class CompanySerializer(serializers.ModelSerializer):
    tarif = TarifSerializer()
    class Meta:
        model = Company
        fields = ['id', 'name', 'phone', 'working_day', 'start_date', 'end_date', 'is_active', 'created', 'tarif']


class TarifCompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = TarifCompany
        fields = ['id', 'name', 'status', 'amount', 'created', 'is_active']


class TeacherSerializer(serializers.ModelSerializer):
    tarif = TarifCompanySerializer()

    class Meta:
        model = Teacher
        fields = ['id', 'username', 'phone', 'type', 'tarif', 'is_payment', 'is_salary', 'is_main', 'is_child', 'company']


class GroupSerializer(serializers.ModelSerializer):
    teacher = TeacherSerializer()
    helper = TeacherSerializer()

    class Meta:
        model = Group
        fields = ['id', 'name', 'company', 'teacher', 'helper', 'is_active']


class ChildSerializer(serializers.ModelSerializer):
    # tarif = TarifCompanySerializer()
    # group = GroupSerializer()

    class Meta:
        model = Child
        fields = ['id', 'name', 'tarif', 'birth_date', 'phone', 'status', 'group', 'is_active', 'company']


class AttendanceSerializer(serializers.ModelSerializer):
    child = ChildSerializer()
    teacher = TeacherSerializer()

    class Meta:
        model = Attendance
        fields = ['id', 'company', 'child', 'teacher', 'date', 'presence', 'is_active']


class PaymentCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentCategory
        fields = ['id', 'name', 'company']


class PaymentSerializer(serializers.ModelSerializer):
    child = ChildSerializer()
    teacher = TeacherSerializer()
    category = PaymentCategorySerializer()

    class Meta:
        model = Payment
        fields = ['id', 'company', 'user', 'child', 'teacher', 'category', 'date', 'user_before_cash', 'user_after_cash', 'date_month', 'amount', 'payment_type', 'description', 'is_edit', 'is_active']


class TransferSerializer(serializers.ModelSerializer):
    user = TeacherSerializer()
    teacher_1 = TeacherSerializer()
    teacher_2 = TeacherSerializer()

    class Meta:
        model = Transfer
        fields = ['id', 'company', 'user', 'teacher_1', 'teacher_2', 'teacher_1_before_cash', 'teacher_1_after_cash', 'teacher_2_before_cash', 'teacher_2_after_cash', 'date', 'summa', 'description', 'is_active']


class CashSerializer(serializers.ModelSerializer):
    teacher = TeacherSerializer()

    class Meta:
        model = Cash
        fields = ['id', 'company', 'amount', 'teacher', 'is_active']