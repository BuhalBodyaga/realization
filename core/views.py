from django.shortcuts import render
from django.http import JsonResponse
from django.urls import reverse
from rest_framework import viewsets

from core.distribution_logic import distribute_for_instance
from .models import *
from .serializers import *
from .models import Employee
from .models import Discipline
from .models import Workload
from .models import WorkloadTeacher
from .models import WorkloadDepartment
from django.shortcuts import get_object_or_404
from .forms import (
    EmployeeDisciplineLoadTypeForm,
    EmployeeDisciplineLoadTypeWishForm,
    EmployeeForm,
)
from .forms import DisciplineForm
from .forms import WorkloadForm
from .forms import WorkloadTeacherForm
from .forms import WorkloadDepartmentForm
from .models import EmployeeDisciplineLoadTypeWish
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import user_passes_test
from django.contrib import messages
from django.db.models import Sum


def is_director_or_admin(user):
    return (
        user.groups.filter(name="Директор департамента").exists() or user.is_superuser
    )


def is_teacher(user):
    return user.groups.filter(name="Преподаватель").exists()


def home(request):
    return render(request, "home.html")


def get_available_hours(request):
    employee_id = request.GET.get("employee")
    workload_id = request.GET.get("workload")
    subgroup_id = request.GET.get("subgroup")

    available_hours = None

    if employee_id and workload_id and subgroup_id:
        try:
            employee = Employee.objects.get(id=employee_id)

            department_hours = (
                WorkloadDepartment.objects.filter(
                    workload_id=workload_id, subgroups_id=subgroup_id
                ).aggregate(Sum("hours"))["hours__sum"]
                or 0
            )

            teacher_hours_existing = (
                WorkloadTeacher.objects.filter(
                    workload_id=workload_id, subgroups_id=subgroup_id
                ).aggregate(Sum("hours"))["hours__sum"]
                or 0
            )

            workload_free_hours = department_hours - teacher_hours_existing

            # Ставка преподавателя
            rate = employee.rate.rate_value
            base_hours = 900
            allowed_hours = rate * base_hours

            teacher_total_hours = (
                WorkloadTeacher.objects.filter(employees=employee).aggregate(
                    Sum("hours")
                )["hours__sum"]
                or 0
            )

            rate_free_hours = allowed_hours - teacher_total_hours

            available_hours = min(workload_free_hours, rate_free_hours)

        except Employee.DoesNotExist:
            pass

    return JsonResponse({"available_hours": available_hours})


@login_required
def workload_teacher_detail(request, employee_id):
    semester = int(request.GET.get("semester", 1))
    employee = get_object_or_404(Employee, pk=employee_id)
    workload_teachers = WorkloadTeacher.objects.select_related(
        "workload", "subgroups", "load_type"
    ).filter(
        employees=employee,
        workload__semesters__number=semester
    ).order_by(
        "workload__disciplines__name_of_discipline",
        "workload__groups__name",
        "subgroups__number",
        "load_type__type"
    )
    return render(
        request,
        "workload_teacher_detail.html",
        {
            "employee": employee,
            "workload_teachers": workload_teachers,
            "semester": semester,
        },
    )


@login_required
def workload_teacher_list(request):
    semester = int(request.GET.get("semester", 1))
    employees = Employee.objects.filter(
        workloadteacher__workload__semesters__number=semester
    ).distinct().order_by("surname", "first_name")
    return render(
        request,
        "workload_teacher_list.html",
        {"employees": employees, "semester": semester},
    )


@login_required
@user_passes_test(is_director_or_admin)
def workload_teacher_create(request):
    initial = {}
    if request.method == "GET":
        employee_id = request.GET.get("employee_id")
        workload_id = request.GET.get("workload_id")
        subgroup_id = request.GET.get("subgroup_id")
        max_hours = request.GET.get("max_hours")
        not_assigned = request.GET.get("not_assigned")
        if employee_id:
            initial["employees"] = employee_id
        if workload_id:
            initial["workload"] = workload_id
        if subgroup_id:
            initial["subgroups"] = subgroup_id
        if max_hours and not_assigned:
            initial["hours"] = min(int(max_hours), int(not_assigned))
    if request.method == "POST":
        form = WorkloadTeacherForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Нагрузка преподавателя успешно добавлена!")
            return redirect("workload_teacher_list")
    else:
        form = WorkloadTeacherForm(initial=initial)
    return render(request, "workload_teacher_form.html", {"form": form})


def workload_teacher_update(request, pk):
    workload = get_object_or_404(WorkloadTeacher, pk=pk)
    if request.method == "POST":
        form = WorkloadTeacherForm(request.POST, instance=workload)
        if form.is_valid():
            form.save()
            messages.success(request, "Нагрузка преподавателя успешно обновлена!")
            return redirect("workload_teacher_list")
    else:
        form = WorkloadTeacherForm(instance=workload)
    return render(request, "workload_teacher_form.html", {"form": form})


def workload_teacher_delete(request, pk):
    workload = get_object_or_404(WorkloadTeacher, pk=pk)
    if request.method == "POST":
        workload.delete()
        messages.success(request, "Нагрузка преподавателя успешно удалена!")
        return redirect("workload_teacher_list")
    return render(
        request,
        "workload_teacher_confirm_delete.html",
        {"object": workload, "type": "преподавателя"},
    )


def employee_list(request):
    employees = Employee.objects.all().order_by("surname", "first_name", "second_name")
    return render(request, "employee_list.html", {"employees": employees})


def employee_detail(request, pk):
    employee = get_object_or_404(Employee, pk=pk)
    return render(request, "employee_detail.html", {"employee": employee})


@login_required
@user_passes_test(is_director_or_admin)
def employee_create(request):
    if request.method == "POST":
        form = EmployeeForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Преподаватель успешно добавлен!")
            return redirect("employee_list")
    else:
        form = EmployeeForm()
    return render(request, "employee_form.html", {"form": form})


@login_required
@user_passes_test(is_director_or_admin)
def employee_update(request, pk):
    employee = get_object_or_404(Employee, pk=pk)
    if request.method == "POST":
        form = EmployeeForm(request.POST, instance=employee)
        if form.is_valid():
            form.save()
            messages.success(request, "Преподаватель успешно обновлен!")
            return redirect("employee_list")
    else:
        form = EmployeeForm(instance=employee)
    return render(request, "employee_form.html", {"form": form})


@login_required
@user_passes_test(is_director_or_admin)
def employee_delete(request, pk):
    employee = get_object_or_404(Employee, pk=pk)
    if request.method == "POST":
        employee.delete()
        messages.success(request, "Преподаватель успешно удален!")
        return redirect("employee_list")
    return render(request, "employee_confirm_delete.html", {"employee": employee})


def discipline_list(request):
    disciplines = Discipline.objects.all().order_by("name_of_discipline")
    return render(request, "discipline_list.html", {"disciplines": disciplines})


def discipline_detail(request, pk):
    discipline = get_object_or_404(Discipline, pk=pk)
    return render(request, "discipline_detail.html", {"discipline": discipline})


@login_required
@user_passes_test(is_director_or_admin)
def discipline_create(request):
    if request.method == "POST":
        form = DisciplineForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Дисциплина успешно добавлена!")
            return redirect("discipline_list")
    else:
        form = DisciplineForm()
    return render(request, "discipline_form.html", {"form": form})


@login_required
@user_passes_test(is_director_or_admin)
def discipline_update(request, pk):
    discipline = get_object_or_404(Discipline, pk=pk)
    if request.method == "POST":
        form = DisciplineForm(request.POST, instance=discipline)
        if form.is_valid():
            form.save()
            messages.success(request, "Дисциплина успешно обновлена!")
            return redirect("discipline_list")
    else:
        form = DisciplineForm(instance=discipline)
    return render(request, "discipline_form.html", {"form": form})


@login_required
@user_passes_test(is_director_or_admin)
def discipline_delete(request, pk):
    discipline = get_object_or_404(Discipline, pk=pk)
    if request.method == "POST":
        discipline.delete()
        messages.success(request, "Дисциплина успешно удалена!")
        return redirect("discipline_list")
    return render(request, "discipline_confirm_delete.html", {"discipline": discipline})


def workload_list(request):
    semester = int(request.GET.get("semester", 1))
    workloads = Workload.objects.filter(semesters__number=semester).order_by(
        "groups__name", "disciplines__name_of_discipline"
    )
    return render(
        request,
        "workload_list.html",
        {
            "workloads": workloads,
            "semester": semester,
        },
    )


def workload_detail(request, pk):
    workload = get_object_or_404(Workload, pk=pk)
    if request.method == "POST":
        form = WorkloadForm(request.POST, instance=workload)
        if form.is_valid():
            workload = form.save()
            form.save_m2m()
            messages.success(request, "Типы нагрузки обновлены!")
            return redirect("workload_detail", pk=pk)
    else:
        form = WorkloadForm(instance=workload)
    group = workload.groups
    count_subgroups = (group.count_people // 15) + (1 if group.count_people % 15 else 0)
    return render(
        request,
        "workload_detail.html",
        {
            "workload": workload,
            "form": form,
            "count_subgroups": count_subgroups,
        },
    )


@login_required
@user_passes_test(is_director_or_admin)
def workload_create(request):
    if request.method == "POST":
        form = WorkloadForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Нагрузка успешно добавлена!")
            return redirect("workload_list")
    else:
        form = WorkloadForm()
    return render(request, "workload_form.html", {"form": form})


@login_required
@user_passes_test(is_director_or_admin)
def workload_update(request, pk):
    workload = get_object_or_404(Workload, pk=pk)
    if request.method == "POST":
        form = WorkloadForm(request.POST, instance=workload)
        if form.is_valid():
            form.save()
            messages.success(request, "Нагрузка успешно обновлена!")
            return redirect("workload_list")
    else:
        form = WorkloadForm(instance=workload)
    return render(request, "workload_form.html", {"form": form})


@login_required
@user_passes_test(is_director_or_admin)
def workload_delete(request, pk):
    workload = get_object_or_404(Workload, pk=pk)
    if request.method == "POST":
        workload.delete()
        messages.success(request, "Нагрузка успешно удалена!")
        return redirect("workload_list")
    return render(request, "workload_confirm_delete.html", {"workload": workload})


from django.views.decorators.csrf import csrf_exempt


@csrf_exempt
def workload_department_list(request):
    semester = int(request.GET.get("semester", 1))
    disciplines = Discipline.objects.all().order_by("name_of_discipline")
    groups = Group.objects.all()
    subgroups = Subgroup.objects.all()

    selected_discipline_id = request.GET.get("discipline") or request.POST.get(
        "discipline"
    )
    selected_load_type_id = (
        request.POST.get("load_type") if request.method == "POST" else None
    )

    if selected_discipline_id:
        load_types = LoadType.objects.filter(
            workload__disciplines_id=selected_discipline_id,
            workload__semesters__number=semester,
        ).distinct()
    else:
        load_types = LoadType.objects.none()

    if request.method == "POST":
        hours = request.POST.get("hours")
        group_id = request.POST.get("group")
        subgroup_id = request.POST.get("subgroup")

        if (
            selected_discipline_id
            and selected_load_type_id
            and hours
            and group_id
            and subgroup_id
        ):
            discipline = Discipline.objects.get(pk=selected_discipline_id)
            load_type = LoadType.objects.get(pk=selected_load_type_id)
            group = Group.objects.get(pk=group_id)
            subgroup = Subgroup.objects.get(pk=subgroup_id)
            semester_obj = Semester.objects.get(number=semester)
            workload, created = Workload.objects.get_or_create(
                disciplines=discipline,
                semesters=semester_obj,
                groups=group,
            )
            workload.load_types.add(load_type)
            workload.save()

            wd, created = WorkloadDepartment.objects.get_or_create(
                workload=workload,
                subgroups=subgroup,
                load_type=load_type,
                defaults={"hours": int(hours)},
            )
            if not created:
                wd.hours += int(hours)
                wd.save()
                messages.success(request, "Часы добавлены к существующей записи!")
            else:
                messages.success(request, "Нагрузка добавлена!")
            return redirect(
                request.path
                + f"?semester={semester}&discipline={selected_discipline_id}"
            )

    workloads = WorkloadDepartment.objects.filter(workload__semesters__number=semester)
    report = []
    for wd in workloads:
        total_hours_teachers = (
            WorkloadTeacher.objects.filter(
                workload=wd.workload,
                subgroups=wd.subgroups,
                load_type=wd.load_type,
            ).aggregate(Sum("hours"))["hours__sum"]
            or 0
        )
        report.append(
            {
                "discipline": wd.workload.disciplines.name_of_discipline,
                "load_type": wd.load_type.type,
                "group": wd.workload.groups.name,
                "subgroup": wd.subgroups.number,
                "total_hours_department": wd.hours,
                "total_hours_teachers": total_hours_teachers,
                "remaining_hours": wd.hours - total_hours_teachers,
            }
        )

    return render(
        request,
        "workload_department_list.html",
        {
            "report": report,
            "semester": semester,
            "disciplines": disciplines,
            "load_types": load_types,
            "groups": groups,
            "subgroups": subgroups,
            "selected_discipline_id": selected_discipline_id,
            "selected_load_type_id": selected_load_type_id,
        },
    )


def workload_department_detail(request, pk):
    obj = get_object_or_404(WorkloadDepartment, pk=pk)
    return render(
        request, "workload_department_detail.html", {"workload_department": obj}
    )


def workload_department_create(request):
    if request.method == "POST":
        form = WorkloadDepartmentForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("workload_department_list")
    else:
        form = WorkloadDepartmentForm()
    return render(request, "workload_department_form.html", {"form": form})


def workload_department_update(request, pk):
    workload = get_object_or_404(WorkloadDepartment, pk=pk)
    if request.method == "POST":
        form = WorkloadDepartmentForm(request.POST, instance=workload)
        if form.is_valid():
            form.save()
            return redirect("workload_department_list")
    else:
        form = WorkloadDepartmentForm(instance=workload)
    return render(request, "workload_department_update.html", {"form": form})


def workload_department_delete(request, pk):
    workload = get_object_or_404(WorkloadDepartment, pk=pk)
    if request.method == "POST":
        workload.delete()
        return redirect("workload_department_list")
    return render(
        request,
        "workload_department_confirm_delete.html",
        {"object": workload, "type": "департамента"},
    )


@login_required
@user_passes_test(is_director_or_admin)
def employee_loadtype_matrix(request, pk):
    employee = get_object_or_404(Employee, pk=pk)
    if request.method == "POST":
        form = EmployeeDisciplineLoadTypeForm(request.POST, employee=employee)
        if form.is_valid():
            EmployeeDisciplineLoadType.objects.filter(employee=employee).delete()
            for discipline in form.disciplines:
                for load_type in form.load_types:
                    field_name = f"disc_{discipline.id}_lt_{load_type.id}"
                    if form.cleaned_data.get(field_name):
                        EmployeeDisciplineLoadType.objects.create(
                            employee=employee,
                            discipline=discipline,
                            load_type=load_type,
                        )
            messages.success(request, "Сохранено!")
            return redirect("employee_detail", pk=employee.pk)
    else:
        form = EmployeeDisciplineLoadTypeForm(employee=employee)
    return render(
        request, "employee_loadtype_matrix.html", {"form": form, "employee": employee}
    )


@login_required
def employee_loadtype_matrix_wish(request, pk):
    employee = get_object_or_404(Employee, pk=pk)
    if request.method == "POST":
        form = EmployeeDisciplineLoadTypeWishForm(request.POST, employee=employee)
        if form.is_valid():
            EmployeeDisciplineLoadTypeWish.objects.filter(employee=employee).delete()
            for discipline in form.disciplines:
                for load_type in form.load_types:
                    field_name = f"disc_{discipline.id}_lt_{load_type.id}"
                    if form.cleaned_data.get(field_name):
                        EmployeeDisciplineLoadTypeWish.objects.create(
                            employee=employee,
                            discipline=discipline,
                            load_type=load_type,
                        )
            messages.success(request, "Сохранено!")
            return redirect("employee_detail", pk=employee.pk)
    else:
        form = EmployeeDisciplineLoadTypeWishForm(employee=employee)
    return render(
        request,
        "employee_loadtype_matrix_wish.html",
        {"form": form, "employee": employee},
    )


def distribute_department_load(request):
    if request.method == "POST":
        semester = int(request.GET.get("semester", 1))
        wds = WorkloadDepartment.objects.filter(workload__semesters__number=semester)
        count = 0
        for wd in wds:
            distribute_for_instance(wd)
            count += 1
        messages.success(
            request, f"Распределение выполнено для {count} записей семестра {semester}!"
        )
    return redirect(f"{reverse('workload_department_list')}?semester={semester}")


class DegreeViewSet(viewsets.ModelViewSet):
    queryset = Degree.objects.all()
    serializer_class = DegreeSerializer


class RankViewSet(viewsets.ModelViewSet):
    queryset = Rank.objects.all()
    serializer_class = RankSerializer


class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer


class RateViewSet(viewsets.ModelViewSet):
    queryset = Rate.objects.all()
    serializer_class = RateSerializer


class EmployeeViewSet(viewsets.ModelViewSet):
    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer


class GroupViewSet(viewsets.ModelViewSet):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer


class SubgroupViewSet(viewsets.ModelViewSet):
    queryset = Subgroup.objects.all()
    serializer_class = SubgroupSerializer


class SemesterViewSet(viewsets.ModelViewSet):
    queryset = Semester.objects.all()
    serializer_class = SemesterSerializer


class LoadTypeViewSet(viewsets.ModelViewSet):
    queryset = LoadType.objects.all()
    serializer_class = LoadTypeSerializer


class DisciplineTypeViewSet(viewsets.ModelViewSet):
    queryset = DisciplineType.objects.all()
    serializer_class = DisciplineTypeSerializer


class DisciplineViewSet(viewsets.ModelViewSet):
    queryset = Discipline.objects.all()
    serializer_class = DisciplineSerializer


class WorkloadViewSet(viewsets.ModelViewSet):
    queryset = Workload.objects.all()
    serializer_class = WorkloadSerializer


class WorkloadTeacherViewSet(viewsets.ModelViewSet):
    queryset = WorkloadTeacher.objects.all()
    serializer_class = WorkloadTeacherSerializer


class WorkloadDepartmentViewSet(viewsets.ModelViewSet):
    queryset = WorkloadDepartment.objects.all()
    serializer_class = WorkloadDepartmentSerializer


class DepartmentViewSet(viewsets.ModelViewSet):
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer
