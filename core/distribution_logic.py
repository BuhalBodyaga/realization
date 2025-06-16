from .models import WorkloadTeacher, Employee
from django.db.models import Sum

NORM_HOURS_FULL_RATE = 900

def distribute_for_instance(wd):
    workload = wd.workload
    discipline = workload.disciplines
    subgroup = wd.subgroups

    total_department_hours = wd.hours
    assigned_hours = (
        WorkloadTeacher.objects
        .filter(workload=workload, subgroups=subgroup)
        .aggregate(Sum('hours'))['hours__sum'] or 0
    )

    remaining_hours = total_department_hours - assigned_hours
    if remaining_hours <= 0:
        print("⛔ Нечего распределять, все часы уже распределены.")
        return

    discipline_type = discipline.types_of_discipline
    suitable_employees = Employee.objects.filter(
        discipline_types=discipline_type
    )

    for employee in suitable_employees:
        assigned_to_teacher = (
            WorkloadTeacher.objects
            .filter(employees=employee)
            .aggregate(Sum('hours'))['hours__sum'] or 0
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
