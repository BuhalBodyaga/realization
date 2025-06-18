from .models import WorkloadTeacher, Employee
from django.db.models import Sum

NORM_HOURS_FULL_RATE = 900


def can_employee_teach_loadtype(employee, load_type):
    # Пример: ассистент не может вести лекции
    if employee.post.type.lower() == "ассистент" and load_type.type.lower() == "лекция":
        return False
    return True


def suggest_employees_for_unassigned(discipline, load_type):
    """
    Предлагает преподавателей, которые могут теоретически вести нагрузку по типу и должности.
    """
    suitable = []
    for emp in Employee.objects.all():
        if can_employee_teach_loadtype(emp, load_type):
            suitable.append(emp)
    return suitable


def distribute_for_instance(wd):
    workload = wd.workload
    discipline = workload.disciplines
    subgroup = wd.subgroups
    load_type = workload.load_types

    total_department_hours = wd.hours
    assigned_hours = (
        WorkloadTeacher.objects.filter(workload=workload, subgroups=subgroup).aggregate(
            Sum("hours")
        )["hours__sum"]
        or 0
    )

    remaining_hours = total_department_hours - assigned_hours
    if remaining_hours <= 0:
        print("⛔ Нечего распределять, все часы уже распределены.")
        return

    # 1. Сначала — преподаватель, закреплённый за дисциплиной
    main_employee = Employee.objects.filter(main_discipline=discipline).first()
    candidates = []

    if main_employee and discipline in main_employee.disciplines.all():
        candidates.append(main_employee)

    # 2. Затем — все, кто может вести эту дисциплину
    other_employees = Employee.objects.filter(disciplines=discipline).exclude(
        pk=getattr(main_employee, "pk", None)
    )
    candidates += list(other_employees)

    # 3. Распределяем нагрузку только по этим кандидатам
    for employee in candidates:
        # Проверка: может ли вести данный тип нагрузки (например, ассистент не может вести лекции)
        if not can_employee_teach_loadtype(employee, load_type):
            continue

        assigned_to_teacher = (
            WorkloadTeacher.objects.filter(employees=employee).aggregate(Sum("hours"))[
                "hours__sum"
            ]
            or 0
        )
        allowed = employee.rate.rate_value * NORM_HOURS_FULL_RATE
        free_for_teacher = allowed - assigned_to_teacher

        if free_for_teacher <= 0:
            continue

        hours_to_assign = min(remaining_hours, free_for_teacher)

        WorkloadTeacher.objects.create(
            hours=hours_to_assign,
            subgroups=subgroup,
            workload=workload,
            employees=employee,
        )

        remaining_hours -= hours_to_assign
        print(f"✅ Назначено {hours_to_assign} ч. преподавателю {employee}")
        if remaining_hours <= 0:
            break

    # 4. Если осталась нераспределённая нагрузка — только предлагаем подходящих преподавателей
    if remaining_hours > 0:
        print(f"⚠️ Осталось нераспределённых часов: {remaining_hours}")
        suggested = suggest_employees_for_unassigned(discipline, load_type)
        print("Возможные кандидаты для оставшейся нагрузки:")
        for emp in suggested:
            print(f"- {emp} ({emp.post})")
