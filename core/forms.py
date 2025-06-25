from django import forms
from .models import Employee, EmployeeDisciplineLoadType, EmployeeDisciplineLoadTypeWish
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
            "disciplines",
            "main_discipline",
        ]
        widgets = {
            "first_name": forms.TextInput(attrs={"class": "form-control"}),
            "second_name": forms.TextInput(attrs={"class": "form-control"}),
            "surname": forms.TextInput(attrs={"class": "form-control"}),
            "rank": forms.Select(attrs={"class": "form-select"}),
            "degree": forms.Select(attrs={"class": "form-select"}),
            "post": forms.Select(attrs={"class": "form-select"}),
            "rate": forms.Select(attrs={"class": "form-select"}),
            "disciplines": forms.SelectMultiple(attrs={"class": "form-select"}),
            "main_discipline": forms.SelectMultiple(attrs={"class": "form-select"}),
        }
        labels = {
            "disciplines": "Дисциплины",
            "main_discipline": "Основная дисциплина",
        }

        def clean(self):
            cleaned_data = super().clean()
            disciplines = cleaned_data.get("disciplines")
            main_discipline = cleaned_data.get("main_discipline")
            if main_discipline and disciplines:
                for md in main_discipline.all():
                    if md not in disciplines.all():
                        self.add_error(
                            "main_discipline",
                            "Основная дисциплина должна быть выбрана среди дисциплин, которые может вести преподаватель.",
                        )
            return cleaned_data


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
            "load_types": "Типы нагрузки",
            "groups": "Группа",
            "semesters": "Семестр",
        }
        widgets = {
            "disciplines": forms.Select(attrs={"class": "form-select"}),
            "load_types": forms.CheckboxSelectMultiple(),  # чекбоксы!
            "groups": forms.Select(attrs={"class": "form-select"}),
            "semesters": forms.Select(attrs={"class": "form-select"}),
        }


class WorkloadTeacherForm(forms.ModelForm):
    class Meta:
        model = WorkloadTeacher
        fields = ["employees", "workload", "subgroups", "hours"]
        labels = {
            "employees": "Преподаватель",
            "workload": "Нагрузка (предмет-группа-семестр)",
            "subgroups": "Подгруппа",
            "hours": "Часы",
        }
        widgets = {
            "employees": forms.Select(attrs={"class": "form-select"}),
            "workload": forms.Select(attrs={"class": "form-select"}),
            "subgroups": forms.Select(attrs={"class": "form-select"}),
            "hours": forms.NumberInput(attrs={"class": "form-control"}),
        }


def clean(self):
    cleaned_data = super().clean()
    employee = cleaned_data.get("employees")
    workload = cleaned_data.get("workload")

    if employee and workload:
        discipline = workload.disciplines
        discipline_type = discipline.types_of_discipline

        # Проверка: может ли вести дисциплину этого типа
        if not employee.disciplines.filter(
            types_of_discipline=discipline_type
        ).exists():
            raise ValidationError(
                {
                    "employees": f"Преподаватель {employee} не может вести дисциплины типа '{discipline_type}'."
                }
            )
    return cleaned_data


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


class EmployeeDisciplineLoadTypeForm(forms.Form):
    def __init__(self, *args, **kwargs):
        employee = kwargs.pop('employee')
        super().__init__(*args, **kwargs)
        self.disciplines = employee.disciplines.all()
        self.load_types = LoadType.objects.all()
        self.field_matrix = []
        for discipline in self.disciplines:
            row = []
            for load_type in self.load_types:
                field_name = f"disc_{discipline.id}_lt_{load_type.id}"
                checked = EmployeeDisciplineLoadType.objects.filter(
                    employee=employee, discipline=discipline, load_type=load_type
                ).exists()
                self.fields[field_name] = forms.BooleanField(
                    required=False,
                    initial=checked,
                    label=""
                )
                row.append(field_name)
            self.field_matrix.append((discipline, row))


class EmployeeDisciplineLoadTypeWishForm(forms.Form):
    def __init__(self, *args, **kwargs):
        employee = kwargs.pop('employee')
        super().__init__(*args, **kwargs)
        self.disciplines = employee.disciplines.all()
        self.load_types = LoadType.objects.all()
        self.field_matrix = []
        for discipline in self.disciplines:
            row = []
            for load_type in self.load_types:
                field_name = f"disc_{discipline.id}_lt_{load_type.id}"
                checked = EmployeeDisciplineLoadTypeWish.objects.filter(
                    employee=employee, discipline=discipline, load_type=load_type
                ).exists()
                self.fields[field_name] = forms.BooleanField(
                    required=False,
                    initial=checked,
                    label=""
                )
                row.append(field_name)
            self.field_matrix.append((discipline, row))