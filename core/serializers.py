from rest_framework import serializers
from .models import (
    Degree, Rank, Post, Rate, Employee,
    Group, Subgroup, Semester, LoadType,
    DisciplineType, Discipline, Workload,
    WorkloadTeacher, WorkloadDepartment, Department
)

class DegreeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Degree
        fields = '__all__'

class RankSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rank
        fields = '__all__'

class PostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = '__all__'

class RateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rate
        fields = '__all__'

class EmployeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employee
        fields = '__all__'

class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = '__all__'

class SubgroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subgroup
        fields = '__all__'

class SemesterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Semester
        fields = '__all__'

class LoadTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = LoadType
        fields = '__all__'

class DisciplineTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = DisciplineType
        fields = '__all__'

class DisciplineSerializer(serializers.ModelSerializer):
    class Meta:
        model = Discipline
        fields = '__all__'

class WorkloadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Workload
        fields = '__all__'

class WorkloadTeacherSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkloadTeacher
        fields = '__all__'

class WorkloadDepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkloadDepartment
        fields = '__all__'

class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = '__all__'
