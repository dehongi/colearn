from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.db.models import Q
from .models import Course, Module, Lesson, Suggestion, Enrollment
from .forms import (
    CourseForm,
    ModuleForm,
    LessonForm,
    SuggestionForm,
    SuggestionStatusForm,
)


def course_list(request):
    courses = Course.objects.filter(is_published=True)
    query = request.GET.get("q")
    if query:
        courses = courses.filter(
            Q(title__icontains=query) | Q(description__icontains=query)
        )
    return render(request, "courses/course_list.html", {"courses": courses})


def course_detail(request, slug):
    course = get_object_or_404(Course, slug=slug, is_published=True)
    modules = course.modules.all().order_by("order")
    is_enrolled = False
    if request.user.is_authenticated:
        is_enrolled = Enrollment.objects.filter(
            user=request.user, course=course, is_active=True
        ).exists()
    return render(
        request,
        "courses/course_detail.html",
        {"course": course, "modules": modules, "is_enrolled": is_enrolled},
    )


@login_required
def lesson_detail(request, course_slug, lesson_id):
    course = get_object_or_404(Course, slug=course_slug, is_published=True)
    lesson = get_object_or_404(Lesson, id=lesson_id, module__course=course)
    enrollment = get_object_or_404(
        Enrollment, user=request.user, course=course, is_active=True
    )

    if request.method == "POST":
        form = SuggestionForm(request.POST)
        if form.is_valid():
            suggestion = form.save(commit=False)
            suggestion.lesson = lesson
            suggestion.user = request.user
            suggestion.save()
            messages.success(
                request, _("Your suggestion has been submitted successfully.")
            )
            return redirect(
                "courses:lesson_detail", course_slug=course_slug, lesson_id=lesson_id
            )
    else:
        form = SuggestionForm()

    return render(
        request,
        "courses/lesson_detail.html",
        {"course": course, "lesson": lesson, "form": form},
    )


@login_required
def enroll_course(request, slug):
    course = get_object_or_404(Course, slug=slug, is_published=True)
    if not Enrollment.objects.filter(user=request.user, course=course).exists():
        Enrollment.objects.create(user=request.user, course=course)
        messages.success(
            request, _("You have been enrolled in the course successfully.")
        )
    return redirect("courses:course_detail", slug=slug)


@login_required
def instructor_dashboard(request):
    courses = Course.objects.filter(instructor=request.user)
    return render(request, "courses/instructor_dashboard.html", {"courses": courses})


@login_required
def create_course(request):
    if request.method == "POST":
        form = CourseForm(request.POST, request.FILES)
        if form.is_valid():
            course = form.save(commit=False)
            course.instructor = request.user
            course.save()
            messages.success(request, _("Course created successfully."))
            return redirect("courses:instructor_dashboard")
    else:
        form = CourseForm()
    return render(request, "courses/course_form.html", {"form": form})


@login_required
def edit_course(request, slug):
    course = get_object_or_404(Course, slug=slug, instructor=request.user)
    if request.method == "POST":
        form = CourseForm(request.POST, request.FILES, instance=course)
        if form.is_valid():
            form.save()
            messages.success(request, _("Course updated successfully."))
            return redirect("courses:instructor_dashboard")
    else:
        form = CourseForm(instance=course)
    return render(request, "courses/course_form.html", {"form": form})


@login_required
def manage_suggestions(request):
    suggestions = Suggestion.objects.filter(
        lesson__module__course__instructor=request.user
    )
    if request.method == "POST":
        form = SuggestionStatusForm(request.POST)
        if form.is_valid():
            suggestion = get_object_or_404(
                Suggestion, id=request.POST.get("suggestion_id")
            )
            suggestion.status = form.cleaned_data["status"]
            suggestion.save()
            messages.success(request, _("Suggestion status updated successfully."))
            return redirect("courses:manage_suggestions")
    else:
        form = SuggestionStatusForm()
    return render(
        request,
        "courses/manage_suggestions.html",
        {"suggestions": suggestions, "form": form},
    )


@login_required
def create_module(request, course_slug):
    course = get_object_or_404(Course, slug=course_slug, instructor=request.user)
    if request.method == "POST":
        form = ModuleForm(request.POST)
        if form.is_valid():
            module = form.save(commit=False)
            module.course = course
            module.save()
            messages.success(request, _("Module created successfully."))
            return redirect("courses:course_detail", slug=course_slug)
    else:
        form = ModuleForm()
    return render(
        request,
        "courses/module_form.html",
        {"form": form, "course": course, "title": _("Create Module")},
    )


@login_required
def edit_module(request, course_slug, module_id):
    course = get_object_or_404(Course, slug=course_slug, instructor=request.user)
    module = get_object_or_404(Module, id=module_id, course=course)
    if request.method == "POST":
        form = ModuleForm(request.POST, instance=module)
        if form.is_valid():
            form.save()
            messages.success(request, _("Module updated successfully."))
            return redirect("courses:course_detail", slug=course_slug)
    else:
        form = ModuleForm(instance=module)
    return render(
        request,
        "courses/module_form.html",
        {"form": form, "course": course, "module": module, "title": _("Edit Module")},
    )


@login_required
def delete_module(request, course_slug, module_id):
    course = get_object_or_404(Course, slug=course_slug, instructor=request.user)
    module = get_object_or_404(Module, id=module_id, course=course)
    if request.method == "POST":
        module.delete()
        messages.success(request, _("Module deleted successfully."))
        return redirect("courses:course_detail", slug=course_slug)
    return render(
        request,
        "courses/confirm_delete.html",
        {"object": module, "title": _("Delete Module")},
    )


@login_required
def create_lesson(request, course_slug, module_id):
    course = get_object_or_404(Course, slug=course_slug, instructor=request.user)
    module = get_object_or_404(Module, id=module_id, course=course)
    if request.method == "POST":
        form = LessonForm(request.POST)
        if form.is_valid():
            lesson = form.save(commit=False)
            lesson.module = module
            lesson.save()
            messages.success(request, _("Lesson created successfully."))
            return redirect("courses:course_detail", slug=course_slug)
    else:
        form = LessonForm()
    return render(
        request,
        "courses/lesson_form.html",
        {"form": form, "course": course, "module": module, "title": _("Create Lesson")},
    )


@login_required
def edit_lesson(request, course_slug, module_id, lesson_id):
    course = get_object_or_404(Course, slug=course_slug, instructor=request.user)
    module = get_object_or_404(Module, id=module_id, course=course)
    lesson = get_object_or_404(Lesson, id=lesson_id, module=module)
    if request.method == "POST":
        form = LessonForm(request.POST, instance=lesson)
        if form.is_valid():
            form.save()
            messages.success(request, _("Lesson updated successfully."))
            return redirect("courses:course_detail", slug=course_slug)
    else:
        form = LessonForm(instance=lesson)
    return render(
        request,
        "courses/lesson_form.html",
        {
            "form": form,
            "course": course,
            "module": module,
            "lesson": lesson,
            "title": _("Edit Lesson"),
        },
    )


@login_required
def delete_lesson(request, course_slug, module_id, lesson_id):
    course = get_object_or_404(Course, slug=course_slug, instructor=request.user)
    module = get_object_or_404(Module, id=module_id, course=course)
    lesson = get_object_or_404(Lesson, id=lesson_id, module=module)
    if request.method == "POST":
        lesson.delete()
        messages.success(request, _("Lesson deleted successfully."))
        return redirect("courses:course_detail", slug=course_slug)
    return render(
        request,
        "courses/confirm_delete.html",
        {"object": lesson, "title": _("Delete Lesson")},
    )
