
from main.models import Teacher
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
    class Meta:
        models = Teacher
        fields = ['company', 'username', 'get_type_dsplay']