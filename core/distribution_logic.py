from .models import WorkloadTeacher, Employee
from django.db.models import Sum

NORM_HOURS_FULL_RATE = 900

def can_employee_teach_loadtype(employee, load_type):
    # Пример: ассистент не может вести лекции
    if employee.post.type.lower() == "ассистент" and load_type.type.lower() == "лекция":
        return False
    return True

def suggest_employees_for_unassigned(discipline, load_type):
    suitable = []
    for emp in Employee.objects.all():
        if can_employee_teach_loadtype(emp, load_type):
            suitable.append(emp)
    return suitable

def distribute_for_instance(wd):
    workload = wd.workload
    discipline = workload.disciplines
    subgroup = wd.subgroups
    load_type = wd.load_type

    total_department_hours = wd.hours
    assigned_hours = (
        WorkloadTeacher.objects.filter(
            workload=workload,
            subgroups=subgroup,
            load_type=load_type,
        ).aggregate(Sum("hours"))["hours__sum"] or 0
    )

    remaining_hours = total_department_hours - assigned_hours
    if remaining_hours <= 0:
        print("⛔ Нечего распределять, все часы уже распределены.")
        return

    # Кандидаты (основные + остальные)
    main_employees = Employee.objects.filter(main_discipline=discipline, disciplines=discipline)
    other_employees = Employee.objects.filter(disciplines=discipline).exclude(
        pk__in=[e.pk for e in main_employees]
    )
    candidates = list(main_employees) + list(other_employees)

    for employee in candidates:
        if not can_employee_teach_loadtype(employee, load_type):
            continue

        assigned_to_teacher = (
            WorkloadTeacher.objects.filter(employees=employee).aggregate(Sum("hours"))["hours__sum"] or 0
        )
        allowed = employee.rate.rate_value * NORM_HOURS_FULL_RATE
        free_for_teacher = allowed - assigned_to_teacher

        if free_for_teacher <= 0 or remaining_hours <= 0:
            continue

        wt_obj, created = WorkloadTeacher.objects.get_or_create(
            workload=workload,
            subgroups=subgroup,
            employees=employee,
            load_type=load_type,
            defaults={"hours": 0},
        )

        hours_to_assign = min(remaining_hours, free_for_teacher)
        if hours_to_assign <= 0:
            continue

        wt_obj.hours += hours_to_assign
        wt_obj.save()

        remaining_hours -= hours_to_assign
        print(f"✅ Назначено {hours_to_assign} ч. преподавателю {employee} ({load_type})")

        if remaining_hours <= 0:
            break

    if remaining_hours > 0:
        print(f"⚠️ Осталось нераспределённых часов: {remaining_hours}")