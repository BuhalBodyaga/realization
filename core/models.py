from django.db import models


class Degree(models.Model):
    type = models.CharField(max_length=45)

    def __str__(self):
        return self.type


class Rank(models.Model):
    type = models.CharField(max_length=45)

    def __str__(self):
        return self.type


class Post(models.Model):
    type = models.CharField(max_length=45)

    def __str__(self):
        return self.type


class Rate(models.Model):
    rate_value = models.FloatField()

    def __str__(self):
        return str(self.rate_value)


class DisciplineType(models.Model):
    type = models.CharField(max_length=100)

    def __str__(self):
        return self.type


class Employee(models.Model):
    first_name = models.CharField("Имя", max_length=100, null=True, blank=True)
    second_name = models.CharField("Отчество", max_length=100, null=True, blank=True)
    surname = models.CharField("Фамилия", max_length=100, null=True, blank=True)
    rank = models.ForeignKey(
        Rank, verbose_name="Ранг", on_delete=models.CASCADE, null=True, blank=True
    )
    degree = models.ForeignKey(
        Degree, verbose_name="Степень", on_delete=models.CASCADE, null=True, blank=True
    )
    post = models.ForeignKey(Post, verbose_name="Должность", on_delete=models.CASCADE)
    rate = models.ForeignKey(Rate, verbose_name="Ставка", on_delete=models.CASCADE)

    disciplines = models.ManyToManyField(
        "Discipline",
        related_name="employees",
        blank=True,
        verbose_name="Дисциплины, которые может вести",
    )
    main_discipline = models.ForeignKey(
        "Discipline",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="main_employees",
        verbose_name="Основная дисциплина",
    )

    def __str__(self):
        return f"{self.surname} {self.first_name[0]}.{self.second_name[0]}."


class Group(models.Model):
    name = models.CharField(max_length=45)
    count_people = models.IntegerField()

    def __str__(self):
        return self.name


class Subgroup(models.Model):
    number = models.IntegerField()

    def __str__(self):
        return f"Подгруппа {self.number}"


class Semester(models.Model):
    number = models.IntegerField()

    def __str__(self):
        return f"Семестр {self.number}"


class LoadType(models.Model):
    type = models.CharField(max_length=45)

    def __str__(self):
        return self.type


class Discipline(models.Model):
    name_of_discipline = models.CharField(max_length=100)
    types_of_discipline = models.ForeignKey(DisciplineType, on_delete=models.CASCADE)

    def __str__(self):
        return self.name_of_discipline


class Workload(models.Model):
    disciplines = models.ForeignKey(Discipline, on_delete=models.CASCADE)
    load_types = models.ManyToManyField(LoadType)  # изменено!
    groups = models.ForeignKey(Group, on_delete=models.CASCADE)
    semesters = models.ForeignKey(Semester, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.disciplines} - {self.groups} - {self.semesters}"


class WorkloadTeacher(models.Model):
    hours = models.IntegerField()
    subgroups = models.ForeignKey(Subgroup, on_delete=models.CASCADE)
    workload = models.ForeignKey(Workload, on_delete=models.CASCADE)
    employees = models.ForeignKey(Employee, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.employees} ({self.hours} ч.)"


class WorkloadDepartment(models.Model):
    hours = models.IntegerField()
    subgroups = models.ForeignKey(Subgroup, on_delete=models.CASCADE)
    workload = models.ForeignKey(Workload, on_delete=models.CASCADE)

    def __str__(self):
        return f"Кафедра — {self.workload} ({self.hours} ч.)"


class Department(models.Model):
    name = models.CharField(max_length=100)
    workload_department = models.ForeignKey(
        WorkloadDepartment, on_delete=models.CASCADE
    )

    def __str__(self):
        return self.name


class EmployeeDisciplineLoadType(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    discipline = models.ForeignKey(Discipline, on_delete=models.CASCADE)
    load_type = models.ForeignKey(LoadType, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('employee', 'discipline', 'load_type')


class EmployeeDisciplineLoadTypeWish(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    discipline = models.ForeignKey(Discipline, on_delete=models.CASCADE)
    load_type = models.ForeignKey(LoadType, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('employee', 'discipline', 'load_type')