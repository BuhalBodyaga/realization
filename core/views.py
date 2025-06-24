from django.shortcuts import render
from django.http import JsonResponse
from rest_framework import viewsets
from .models import *
from .serializers import *
from .models import Employee
from .models import Discipline
from .models import Workload
from .models import WorkloadTeacher
from .models import WorkloadDepartment
from django.shortcuts import get_object_or_404
from .forms import EmployeeDisciplineLoadTypeForm, EmployeeDisciplineLoadTypeWishForm, EmployeeForm
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


def workload_teacher_detail(request, pk):
    obj = get_object_or_404(WorkloadTeacher, pk=pk)
    return render(request, "workload_teacher_detail.html", {"workload_teacher": obj})


@login_required
def workload_teacher_list(request):
    workload_teachers = WorkloadTeacher.objects.select_related(
        "employees", "workload", "subgroups"
    )
    return render(
        request, "workload_teacher_list.html", {"workload_teachers": workload_teachers}
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
    employees = Employee.objects.all()
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
    disciplines = Discipline.objects.all()
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
    workloads = Workload.objects.all()
    return render(request, "workload_list.html", {"workloads": workloads})


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
    # Для отображения количества подгрупп:
    group = workload.groups
    count_subgroups = (group.count_people // 15) + (1 if group.count_people % 15 else 0)
    return render(request, "workload_detail.html", {
        "workload": workload,
        "form": form,
        "count_subgroups": count_subgroups,
    })


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


def workload_department_list(request):
    workload_departments = WorkloadDepartment.objects.select_related(
        "workload", "subgroups"
    )

    report = []

    disciplines = Discipline.objects.all()

    for discipline in disciplines:
        total_hours_department = (
            WorkloadDepartment.objects.filter(
                workload__disciplines=discipline
            ).aggregate(Sum("hours"))["hours__sum"]
            or 0
        )

        total_hours_teachers = (
            WorkloadTeacher.objects.filter(workload__disciplines=discipline).aggregate(
                Sum("hours")
            )["hours__sum"]
            or 0
        )

        remaining_hours = total_hours_department - total_hours_teachers

        details = []
        for wd in WorkloadDepartment.objects.filter(workload__disciplines=discipline):
            teachers = WorkloadTeacher.objects.filter(
                workload=wd.workload, subgroups=wd.subgroups
            )
            teachers_info = [
                {
                    "employee": t.employees,
                    "hours": t.hours,
                }
                for t in teachers
            ]
            assigned_hours = sum(t["hours"] for t in teachers_info)
            not_assigned = wd.hours - assigned_hours

            discipline_type = wd.workload.disciplines.types_of_discipline

            recommended = []
            for emp in Employee.objects.all():
                if emp.disciplines.filter(types_of_discipline=discipline_type).exists():
                    total = (
                        WorkloadTeacher.objects.filter(employees=emp).aggregate(
                            Sum("hours")
                        )["hours__sum"]
                        or 0
                    )
                    allowed = emp.rate.rate_value * 900
                    free = allowed - total
                    if free > 0:
                        recommended.append(
                            {
                                "employee": emp,
                                "free_hours": free,
                            }
                        )

            details.append(
                {
                    "wd": wd,
                    "teachers_info": teachers_info,
                    "not_assigned": not_assigned,
                    "recommended": recommended,
                }
            )

        if total_hours_department > 0:
            report.append(
                {
                    "discipline": discipline.name_of_discipline,
                    "total_hours_department": total_hours_department,
                    "total_hours_teachers": total_hours_teachers,
                    "remaining_hours": remaining_hours,
                    "details": details,
                }
            )

    return render(
        request,
        "workload_department_list.html",
        {
            "workload_departments": workload_departments,
            "report": report,
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
            # Удаляем старые связи
            EmployeeDisciplineLoadType.objects.filter(employee=employee).delete()
            # Добавляем новые
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
    return render(request, "employee_loadtype_matrix.html", {"form": form, "employee": employee})


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
    return render(request, "employee_loadtype_matrix_wish.html", {"form": form, "employee": employee})


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
