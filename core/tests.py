from django.test import TestCase
from django.urls import reverse
from .models import (
    Degree,
    Employee,
    Discipline,
    Group,
    Post,
    Rank,
    Rate,
    Semester,
    DisciplineType,
)
from django.contrib.auth.models import User


class ModelTests(TestCase):
    def setUp(self):
        self.discipline_type = DisciplineType.objects.create(type="Общий")
        self.post = Post.objects.create(type="Доцент")
        self.rate = Rate.objects.create(rate_value=1.0)
        self.rank = Rank.objects.create(type="Кандидат наук")
        self.degree = Degree.objects.create(type="Магистр")

    def test_create_employee(self):
        emp = Employee.objects.create(
            surname="Иванов",
            first_name="Иван",
            second_name="Иванович",
            post=self.post,
            rate=self.rate,
            rank=self.rank,
            degree=self.degree,
        )
        self.assertEqual(emp.surname, "Иванов")
        self.assertEqual(emp.first_name, "Иван")
        self.assertIn("Иванов", str(emp))

    def test_create_discipline(self):
        disc = Discipline.objects.create(
            name_of_discipline="Математика", types_of_discipline=self.discipline_type
        )
        self.assertEqual(disc.name_of_discipline, "Математика")
        self.assertIn("Математика", str(disc))

    def test_create_group_and_semester(self):
        group = Group.objects.create(name="Группа 101", count_people=25)
        semester = Semester.objects.create(number=1)
        self.assertEqual(group.name, "Группа 101")
        self.assertEqual(semester.number, 1)


class ViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="admin", password="12345", is_superuser=True
        )
        self.client.login(username="admin", password="12345")
        self.discipline_type = DisciplineType.objects.create(type="Общий")
        self.post = Post.objects.create(type="Доцент")
        self.rate = Rate.objects.create(rate_value=1.0)
        self.rank = Rank.objects.create(type="Кандидат наук")
        self.degree = Degree.objects.create(type="Магистр")
        self.employee = Employee.objects.create(
            surname="Иванов",
            first_name="Иван",
            second_name="Иванович",
            post=self.post,
            rate=self.rate,
            rank=self.rank,
            degree=self.degree,
        )
        self.discipline = Discipline.objects.create(
            name_of_discipline="Математика", types_of_discipline=self.discipline_type
        )

    def test_employee_list_view(self):
        url = reverse("employee_list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_discipline_list_view(self):
        url = reverse("discipline_list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_workload_list_view(self):
        url = reverse("workload_list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_create_employee_via_post(self):
        url = reverse("employee_create")
        data = {
            "surname": "Петров",
            "first_name": "Петр",
            "second_name": "Петрович",
            "post": self.post.id,
            "rate": self.rate.id,
            "rank": self.rank.id,
            "degree": self.degree.id,
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)  # редирект после успешного создания
        self.assertTrue(Employee.objects.filter(surname="Петров").exists())

    def test_create_discipline_via_post(self):
        url = reverse("discipline_create")
        data = {
            "name_of_discipline": "Физика",
            "types_of_discipline": self.discipline_type.id,
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Discipline.objects.filter(name_of_discipline="Физика").exists())

    def test_delete_employee(self):
        emp = Employee.objects.create(
            surname="Удаляемый",
            first_name="Тест",
            second_name="Тестович",
            post=self.post,
            rate=self.rate,
            rank=self.rank,
            degree=self.degree,
        )
        url = reverse("employee_delete", args=[emp.id])
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Employee.objects.filter(id=emp.id).exists())

    def test_delete_discipline(self):
        disc = Discipline.objects.create(
            name_of_discipline="Удаляемая дисциплина",
            types_of_discipline=self.discipline_type,
        )
        url = reverse("discipline_delete", args=[disc.id])
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Discipline.objects.filter(id=disc.id).exists())

    def test_discipline_create_invalid(self):
        url = reverse("discipline_create")
        data = {
            "name_of_discipline": "",
            "types_of_discipline": "",
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "This field is required.", status_code=200)
