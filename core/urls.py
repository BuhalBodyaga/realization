from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import *
from .views import home
from django.contrib.auth import views as auth_views
from . import views

router = DefaultRouter()
router.register(r"degree", DegreeViewSet)
router.register(r"rank", RankViewSet)
router.register(r"post", PostViewSet)
router.register(r"rate", RateViewSet)
router.register(r"employee", EmployeeViewSet)
router.register(r"group", GroupViewSet)
router.register(r"subgroup", SubgroupViewSet)
router.register(r"semester", SemesterViewSet)
router.register(r"loadtype", LoadTypeViewSet)
router.register(r"disciplinetype", DisciplineTypeViewSet)
router.register(r"discipline", DisciplineViewSet)
router.register(r"workload", WorkloadViewSet)
router.register(r"workloadteacher", WorkloadTeacherViewSet)
router.register(r"workloaddepartment", WorkloadDepartmentViewSet)
router.register(r"department", DepartmentViewSet)

urlpatterns = [
    path("api/", include(router.urls)),
    path("", home, name="home"),
    path("employees/", employee_list, name="employee_list"),
    path("employees/<int:pk>/", employee_detail, name="employee_detail"),
    path("employees/add/", employee_create, name="employee_create"),
    path("employees/<int:pk>/edit/", employee_update, name="employee_update"),
    path("employees/<int:pk>/delete/", employee_delete, name="employee_delete"),
    path("disciplines/", discipline_list, name="discipline_list"),
    path("disciplines/<int:pk>/", discipline_detail, name="discipline_detail"),
    path("disciplines/add/", discipline_create, name="discipline_create"),
    path("disciplines/<int:pk>/edit/", discipline_update, name="discipline_update"),
    path("disciplines/<int:pk>/delete/", discipline_delete, name="discipline_delete"),
    path("workloads/", workload_list, name="workload_list"),
    path("workloads/<int:pk>/", workload_detail, name="workload_detail"),
    path("workloads/add/", workload_create, name="workload_create"),
    path("workloads/<int:pk>/edit/", workload_update, name="workload_update"),
    path("workloads/<int:pk>/delete/", workload_delete, name="workload_delete"),
    path("workload_teacher/", views.workload_teacher_list, name="workload_teacher_list"),    path("workload_teacher/<int:employee_id>/", views.workload_teacher_detail, name="workload_teacher_detail"),
    path(
        "workload_teacher/create/",
        workload_teacher_create,
        name="workload_teacher_create",
    ),
    path(
        "workload_teacher/<int:pk>/edit/",
        workload_teacher_update,
        name="workload_teacher_update",
    ),
    path(
        "workload_teacher/<int:pk>/delete/",
        workload_teacher_delete,
        name="workload_teacher_delete",
    ),
    path(
        "workload_department/",
        workload_department_list,
        name="workload_department_list",
    ),
    path(
        "workload_department/<int:pk>/",
        views.workload_department_detail,
        name="workload_department_detail",
    ),
    path(
        "workload_department/add/",
        views.workload_department_create,
        name="workload_department_create",
    ),
    path(
        "workload_department/<int:pk>/edit/",
        views.workload_department_update,
        name="workload_department_update",
    ),
    path(
        "workload_department/<int:pk>/delete/",
        views.workload_department_delete,
        name="workload_department_delete",
    ),
    path("get-available-hours/", views.get_available_hours, name="get-available-hours"),
    path(
        "login/", auth_views.LoginView.as_view(template_name="login.html"), name="login"
    ),
    path(
        "logout/",
        auth_views.LogoutView.as_view(next_page="employee_list"),
        name="logout",
    ),
    path("employees/<int:pk>/loadtype_matrix/", views.employee_loadtype_matrix, name="employee_loadtype_matrix"),
    path('employees/loadtype_matrix_wish/<int:pk>/', views.employee_loadtype_matrix_wish, name='employee_loadtype_matrix_wish'),
    path("workload_department/distribute/", views.distribute_department_load, name="distribute_department_load"),



]
