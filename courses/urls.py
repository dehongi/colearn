from django.urls import path
from . import views

app_name = "courses"

urlpatterns = [
    # Course list and detail views
    path("", views.course_list, name="course_list"),
    path("<slug:slug>/", views.course_detail, name="course_detail"),
    path("<slug:slug>/enroll/", views.enroll_course, name="enroll_course"),
    # Instructor dashboard and course management
    path(
        "instructor/dashboard/", views.instructor_dashboard, name="instructor_dashboard"
    ),
    path("instructor/course/create/", views.create_course, name="create_course"),
    path("instructor/course/<slug:slug>/edit/", views.edit_course, name="edit_course"),
    path(
        "instructor/suggestions/", views.manage_suggestions, name="manage_suggestions"
    ),
    # Module management
    path(
        "<slug:course_slug>/module/create/", views.create_module, name="create_module"
    ),
    path(
        "<slug:course_slug>/module/<int:module_id>/edit/",
        views.edit_module,
        name="edit_module",
    ),
    path(
        "<slug:course_slug>/module/<int:module_id>/delete/",
        views.delete_module,
        name="delete_module",
    ),
    # Lesson management
    path(
        "<slug:course_slug>/module/<int:module_id>/lesson/create/",
        views.create_lesson,
        name="create_lesson",
    ),
    path(
        "<slug:course_slug>/module/<int:module_id>/lesson/<int:lesson_id>/edit/",
        views.edit_lesson,
        name="edit_lesson",
    ),
    path(
        "<slug:course_slug>/module/<int:module_id>/lesson/<int:lesson_id>/delete/",
        views.delete_lesson,
        name="delete_lesson",
    ),
    path(
        "<slug:course_slug>/lesson/<int:lesson_id>/",
        views.lesson_detail,
        name="lesson_detail",
    ),
]
