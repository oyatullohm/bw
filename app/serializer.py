
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
    type_display = serializers.SerializerMethodField()
    class Meta:
        model = Teacher
        fields = ['company', 'username', 'type_display']
        
    def get_type_display(self, obj):
        return obj.get_type_display()