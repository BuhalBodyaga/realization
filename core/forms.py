from django import forms
from .models import Employee
from .models import Discipline
from .models import Workload
from .models import WorkloadTeacher, WorkloadDepartment
from django.core.exceptions import ValidationError
from django.db.models import Sum


class EmployeeForm(forms.ModelForm):
    class Meta:
        model = Employee
        fields = [
            "first_name",
            "second_name",
            "surname",
            "rank",
            "degree",
            "post",
            "rate",
            "discipline_types",  # ← добавили это поле
        ]
        widgets = {
            "first_name": forms.TextInput(attrs={"class": "form-control"}),
            "second_name": forms.TextInput(attrs={"class": "form-control"}),
            "surname": forms.TextInput(attrs={"class": "form-control"}),
            "rank": forms.Select(attrs={"class": "form-select"}),
            "degree": forms.Select(attrs={"class": "form-select"}),
            "post": forms.Select(attrs={"class": "form-select"}),
            "rate": forms.Select(attrs={"class": "form-select"}),
            "discipline_types": forms.SelectMultiple(attrs={"class": "form-select"}),
        }
        labels = {
            "discipline_types": "Типы дисциплин",
        }


class DisciplineForm(forms.ModelForm):
    class Meta:
        model = Discipline
        fields = ["name_of_discipline", "types_of_discipline"]
        labels = {
            "name_of_discipline": "Название дисциплины",
            "types_of_discipline": "Тип дисциплины",
        }
        widgets = {
            "name_of_discipline": forms.TextInput(attrs={"class": "form-control"}),
            "types_of_discipline": forms.Select(attrs={"class": "form-select"}),
        }


class WorkloadForm(forms.ModelForm):
    class Meta:
        model = Workload
        fields = ["disciplines", "load_types", "groups", "semesters"]
        labels = {
            "disciplines": "Дисциплина",
            "load_types": "Тип нагрузки",
            "groups": "Группа",
            "semesters": "Семестр",
        }
        widgets = {
            "disciplines": forms.Select(attrs={"class": "form-select"}),
            "load_types": forms.Select(attrs={"class": "form-select"}),
            "groups": forms.Select(attrs={"class": "form-select"}),
            "semesters": forms.Select(attrs={"class": "form-select"}),
        }


class WorkloadTeacherForm(forms.ModelForm):
    class Meta:
        model = WorkloadTeacher
        fields = ['employees', 'workload', 'subgroups', 'hours']
        labels = {
            'employees': 'Преподаватель',
            'workload': 'Нагрузка (предмет-группа-семестр)',
            'subgroups': 'Подгруппа',
            'hours': 'Часы',
        }
        widgets = {
            'employees': forms.Select(attrs={'class': 'form-select'}),
            'workload': forms.Select(attrs={'class': 'form-select'}),
            'subgroups': forms.Select(attrs={'class': 'form-select'}),
            'hours': forms.NumberInput(attrs={'class': 'form-control'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        employee = cleaned_data.get('employees')
        workload = cleaned_data.get('workload')

        if employee and workload:
            discipline_type = workload.disciplines.types_of_discipline
            if discipline_type not in employee.discipline_types.all():
                raise ValidationError({
                    'employees': f"Преподаватель {employee} не может вести дисциплину типа '{discipline_type}'."
                })


from django import forms
from .models import WorkloadDepartment, LoadType, Workload


class WorkloadDepartmentForm(forms.ModelForm):
    load_types = forms.ModelChoiceField(
        queryset=LoadType.objects.all(),
        label="Тип нагрузки",
        widget=forms.Select(attrs={"class": "form-select"}),
    )

    class Meta:
        model = WorkloadDepartment
        fields = ["workload", "load_types", "subgroups", "hours"]
        labels = {
            "workload": "Нагрузка",
            "subgroups": "Подгруппа",
            "hours": "Часы",
        }
        widgets = {
            "workload": forms.Select(attrs={"class": "form-select"}),
            "subgroups": forms.Select(attrs={"class": "form-select"}),
            "hours": forms.NumberInput(attrs={"class": "form-control"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            self.fields["load_types"].initial = self.instance.workload.load_types

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.workload.load_types = self.cleaned_data["load_types"]
        if commit:
            instance.workload.save()
            instance.save()
        return instance

    def clean(self):
        cleaned_data = super().clean()
        workload = cleaned_data.get("workload")
        subgroups = cleaned_data.get("subgroups")
        hours = cleaned_data.get("hours")
        employee = cleaned_data.get("employees")

        if workload and subgroups and hours and employee:
            # Проверка по департаменту
            department_hours = (
                WorkloadDepartment.objects.filter(
                    workload=workload, subgroups=subgroups
                ).aggregate(Sum("hours"))["hours__sum"]
                or 0
            )

            teacher_hours_existing = (
                WorkloadTeacher.objects.filter(
                    workload=workload, subgroups=subgroups
                ).aggregate(Sum("hours"))["hours__sum"]
                or 0
            )

            if (teacher_hours_existing + hours) > department_hours:
                raise ValidationError(
                    f"Нельзя назначить {hours} часов: уже распределено {teacher_hours_existing} из {department_hours} доступных часов."
                )

            # Проверка по ставке преподавателя
            rate = employee.rate.rate_value  # 1.0, 0.75, 0.5

            # Например: 1.0 ставка = 450 часов в полгода (примерный норматив)
            base_hours = 450
            allowed_hours = rate * base_hours

            # Считаем всю нагрузку преподавателя
            all_teacher_hours = (
                WorkloadTeacher.objects.filter(employees=employee).aggregate(
                    Sum("hours")
                )["hours__sum"]
                or 0
            )

            if (all_teacher_hours + hours) > allowed_hours:
                raise ValidationError(
                    f"Нельзя назначить {hours} часов. У преподавателя допустимая нагрузка {allowed_hours} ч., уже распределено {all_teacher_hours} ч."
                )

        return cleaned_data
