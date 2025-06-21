from django.contrib import admin
from .models import (
    Degree,
    Rank,
    Post,
    Rate,
    Employee,
    Group,
    Subgroup,
    Semester,
    LoadType,
    DisciplineType,
    Discipline,
    Workload,
    WorkloadTeacher,
    WorkloadDepartment,
    Department,
)


@admin.register(Degree)
class DegreeAdmin(admin.ModelAdmin):
    list_display = ("id", "type")
    search_fields = ("type",)


@admin.register(Rank)
class RankAdmin(admin.ModelAdmin):
    list_display = ("id", "type")
    search_fields = ("type",)


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ("id", "type")
    search_fields = ("type",)


@admin.register(Rate)
class RateAdmin(admin.ModelAdmin):
    list_display = ("id", "rate_value")
    search_fields = ("rate_value",)


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "surname",
        "first_name",
        "second_name",
        "rank",
        "degree",
        "post",
        "rate",
    )
    list_filter = ("rank", "degree", "post", "rate")
    search_fields = ("surname", "first_name", "second_name")


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "count_people")
    search_fields = ("name",)


@admin.register(Subgroup)
class SubgroupAdmin(admin.ModelAdmin):
    list_display = ("id", "number")


@admin.register(Semester)
class SemesterAdmin(admin.ModelAdmin):
    list_display = ("id", "number")


@admin.register(LoadType)
class LoadTypeAdmin(admin.ModelAdmin):
    list_display = ("id", "type")
    search_fields = ("type",)


@admin.register(DisciplineType)
class DisciplineTypeAdmin(admin.ModelAdmin):
    list_display = ("id", "type")
    search_fields = ("type",)


@admin.register(Discipline)
class DisciplineAdmin(admin.ModelAdmin):
    list_display = ("id", "name_of_discipline", "types_of_discipline")
    list_filter = ("types_of_discipline",)
    search_fields = ("name_of_discipline",)


@admin.register(Workload)
class WorkloadAdmin(admin.ModelAdmin):
    list_display = ("id", "disciplines", "groups", "semesters", "load_types")
    list_filter = ("groups", "semesters", "load_types")


@admin.register(WorkloadTeacher)
class WorkloadTeacherAdmin(admin.ModelAdmin):
    list_display = ("id", "employees", "workload", "subgroups", "hours")
    list_filter = ("employees", "workload")


@admin.register(WorkloadDepartment)
class WorkloadDepartmentAdmin(admin.ModelAdmin):
    list_display = ("id", "workload", "subgroups", "hours")
    list_filter = ("workload",)


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "workload_department")
    search_fields = ("name",)
