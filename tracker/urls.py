from django.urls import path

from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("modules/", views.module_list, name="module_list"),
    path("modules/add/", views.module_create, name="module_create"),
    path("modules/<int:pk>/", views.module_detail, name="module_detail"),
    path("modules/<int:pk>/edit/", views.module_edit, name="module_edit"),
    path("assignments/", views.assignment_list, name="assignment_list"),
    path("assignments/add/", views.assignment_create, name="assignment_create"),
    path("assignments/<int:pk>/", views.assignment_detail, name="assignment_detail"),
    path("assignments/<int:pk>/edit/", views.assignment_edit, name="assignment_edit"),
    path("assignments/<int:pk>/archive/", views.assignment_archive, name="assignment_archive"),
]
