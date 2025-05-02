from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.db.models import Q, Avg, Count
from django.utils import timezone
from .models import (
    Course,
    Module,
    Lesson,
    Suggestion,
    Enrollment,
    Category,
    LessonProgress,
    CourseReview,
)
from .forms import (
    CourseForm,
    ModuleForm,
    LessonForm,
    SuggestionForm,
    SuggestionStatusForm,
    CategoryForm,
    LessonProgressForm,
    CourseReviewForm,
)
from django.urls import reverse


def course_list(request):
    courses = Course.objects.filter(is_published=True)
    categories = Category.objects.all()

    # Filter by category
    category_slug = request.GET.get("category")
    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        courses = courses.filter(category=category)

    # Filter by difficulty
    difficulty = request.GET.get("difficulty")
    if difficulty:
        courses = courses.filter(difficulty=difficulty)

    # Filter by price range
    min_price = request.GET.get("min_price")
    max_price = request.GET.get("max_price")
    if min_price:
        try:
            courses = courses.filter(price__gte=float(min_price))
        except ValueError:
            pass
    if max_price:
        try:
            courses = courses.filter(price__lte=float(max_price))
        except ValueError:
            pass

    # Filter by creation date
    time_filter = request.GET.get("time")
    if time_filter:
        now = timezone.now()
        if time_filter == "week":
            courses = courses.filter(created_at__gte=now - timezone.timedelta(days=7))
        elif time_filter == "month":
            courses = courses.filter(created_at__gte=now - timezone.timedelta(days=30))
        elif time_filter == "year":
            courses = courses.filter(created_at__gte=now - timezone.timedelta(days=365))

    # Search
    query = request.GET.get("q")
    if query:
        courses = courses.filter(
            Q(title__icontains=query) | Q(description__icontains=query)
        )

    # Sorting
    sort = request.GET.get("sort")
    if sort == "newest":
        courses = courses.order_by("-created_at")
    elif sort == "oldest":
        courses = courses.order_by("created_at")
    elif sort == "price_low":
        courses = courses.order_by("price")
    elif sort == "price_high":
        courses = courses.order_by("-price")
    else:
        # Default sort by newest
        courses = courses.order_by("-created_at")

    # Add average rating to each course
    for course in courses:
        course.avg_rating = course.enrollments.filter(review__isnull=False).aggregate(
            avg_rating=Avg("review__rating")
        )["avg_rating"]
        course.num_reviews = course.enrollments.filter(review__isnull=False).count()

    return render(
        request,
        "courses/course_list.html",
        {
            "courses": courses,
            "categories": categories,
            "current_filters": {
                "category": category_slug,
                "difficulty": difficulty,
                "min_price": min_price,
                "max_price": max_price,
                "time": time_filter,
                "sort": sort,
                "q": query,
            },
        },
    )


def course_detail(request, slug):
    course = get_object_or_404(Course, slug=slug, is_published=True)
    modules = course.modules.all().order_by("order")
    is_enrolled = False
    enrollment = None
    user_review = None

    if request.user.is_authenticated:
        enrollment = Enrollment.objects.filter(
            user=request.user, course=course, is_active=True
        ).first()
        is_enrolled = enrollment is not None
        if enrollment:
            user_review = CourseReview.objects.filter(enrollment=enrollment).first()

    # Get reviews
    reviews = CourseReview.objects.filter(enrollment__course=course)
    avg_rating = reviews.aggregate(avg_rating=Avg("rating"))["avg_rating"]

    # Handle review submission
    if request.method == "POST" and is_enrolled:
        review_form = CourseReviewForm(request.POST, instance=user_review)
        if review_form.is_valid():
            review = review_form.save(commit=False)
            review.enrollment = enrollment
            review.save()
            messages.success(request, _("Your review has been submitted."))
            return redirect("courses:course_detail", slug=slug)
    else:
        review_form = CourseReviewForm(instance=user_review)

    return render(
        request,
        "courses/course_detail.html",
        {
            "course": course,
            "modules": modules,
            "is_enrolled": is_enrolled,
            "reviews": reviews,
            "avg_rating": avg_rating,
            "review_form": review_form if is_enrolled else None,
            "user_review": user_review,
        },
    )


@login_required
def lesson_detail(request, course_slug, lesson_id):
    course = get_object_or_404(Course, slug=course_slug, is_published=True)
    lesson = get_object_or_404(Lesson, id=lesson_id, module__course=course)
    enrollment = get_object_or_404(
        Enrollment, user=request.user, course=course, is_active=True
    )

    # Track lesson progress
    progress, created = LessonProgress.objects.get_or_create(
        enrollment=enrollment, lesson=lesson
    )

    # Mark lesson as completed if requested
    if request.method == "POST" and "mark_completed" in request.POST:
        progress.is_completed = True
        progress.completed_at = timezone.now()
        progress.save()
        messages.success(request, _("Lesson marked as completed."))
        return redirect(
            "courses:lesson_detail", course_slug=course_slug, lesson_id=lesson_id
        )

    # Handle suggestion submission
    if request.method == "POST" and "suggestion" in request.POST:
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

    # Get previous suggestions for this lesson
    previous_suggestions = (
        Suggestion.objects.filter(lesson=lesson)
        .select_related("user")
        .order_by("-created_at")
    )

    # Get next and previous lessons
    module = lesson.module
    course_modules = course.modules.all().order_by("order")

    # Find all lessons in the course ordered by module order then lesson order
    all_lessons = []
    for m in course_modules:
        all_lessons.extend(list(m.lessons.all().order_by("order")))

    # Get indices for current, next, and previous lessons
    current_index = all_lessons.index(lesson)
    next_lesson = (
        all_lessons[current_index + 1] if current_index < len(all_lessons) - 1 else None
    )
    prev_lesson = all_lessons[current_index - 1] if current_index > 0 else None

    # Calculate course progress
    total_lessons = len(all_lessons)
    completed_lessons = LessonProgress.objects.filter(
        enrollment=enrollment, is_completed=True
    ).count()

    progress_percentage = (
        int((completed_lessons / total_lessons) * 100) if total_lessons > 0 else 0
    )

    return render(
        request,
        "courses/lesson_detail.html",
        {
            "course": course,
            "lesson": lesson,
            "form": form,
            "previous_suggestions": previous_suggestions,
            "next_lesson": next_lesson,
            "prev_lesson": prev_lesson,
            "progress": progress,
            "progress_percentage": progress_percentage,
        },
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

    # For each course, get:
    # - Number of enrollments
    # - Average rating
    # - Number of suggestions pending review

    for course in courses:
        course.enrollment_count = course.enrollments.count()
        course.avg_rating = course.enrollments.filter(review__isnull=False).aggregate(
            avg_rating=Avg("review__rating")
        )["avg_rating"]
        course.pending_suggestions = Suggestion.objects.filter(
            lesson__module__course=course, status=Suggestion.Status.PENDING
        ).count()

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
    # Get courses taught by the instructor
    instructor_courses = Course.objects.filter(
        instructor=request.user
    ).prefetch_related("modules")

    # Filter parameters
    course_filter = request.GET.get("course")
    module_filter = request.GET.get("module")
    status_filter = request.GET.get("status")

    # Base queryset
    suggestions = Suggestion.objects.filter(
        lesson__module__course__instructor=request.user
    ).select_related("lesson", "lesson__module", "lesson__module__course", "user")

    # Apply filters
    if course_filter:
        suggestions = suggestions.filter(lesson__module__course__slug=course_filter)

    if module_filter:
        suggestions = suggestions.filter(lesson__module__id=module_filter)

    if status_filter:
        suggestions = suggestions.filter(status=status_filter)

    # Group suggestions by course for better organization
    courses_with_suggestions = {}
    for suggestion in suggestions:
        course = suggestion.lesson.module.course
        if course not in courses_with_suggestions:
            courses_with_suggestions[course] = []
        courses_with_suggestions[course].append(suggestion)

    # Handle form submission for updating suggestion status
    if request.method == "POST":
        form = SuggestionStatusForm(request.POST)
        if form.is_valid():
            suggestion = get_object_or_404(
                Suggestion, id=request.POST.get("suggestion_id")
            )
            suggestion.status = form.cleaned_data["status"]
            suggestion.instructor_response = form.cleaned_data.get(
                "instructor_response", ""
            )
            suggestion.save()
            messages.success(request, _("Suggestion status updated successfully."))

            # Preserve filters when redirecting
            redirect_url = reverse("courses:manage_suggestions")
            query_params = []
            if course_filter:
                query_params.append(f"course={course_filter}")
            if module_filter:
                query_params.append(f"module={module_filter}")
            if status_filter:
                query_params.append(f"status={status_filter}")

            if query_params:
                redirect_url += "?" + "&".join(query_params)

            return redirect(redirect_url)
    else:
        form = SuggestionStatusForm()

    context = {
        "courses_with_suggestions": courses_with_suggestions,
        "instructor_courses": instructor_courses,
        "form": form,
        "current_course": course_filter,
        "current_module": module_filter,
        "current_status": status_filter,
        "suggestion_statuses": Suggestion.Status.choices,
    }

    return render(
        request,
        "courses/manage_suggestions.html",
        context,
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


@login_required
def manage_categories(request):
    categories = Category.objects.all()
    if request.method == "POST":
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, _("Category created successfully."))
            return redirect("courses:manage_categories")
    else:
        form = CategoryForm()
    return render(
        request,
        "courses/manage_categories.html",
        {"categories": categories, "form": form},
    )


@login_required
def edit_category(request, slug):
    category = get_object_or_404(Category, slug=slug)
    if request.method == "POST":
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request, _("Category updated successfully."))
            return redirect("courses:manage_categories")
    else:
        form = CategoryForm(instance=category)
    return render(
        request,
        "courses/category_form.html",
        {"form": form, "category": category},
    )


@login_required
def delete_category(request, slug):
    category = get_object_or_404(Category, slug=slug)
    if request.method == "POST":
        category.delete()
        messages.success(request, _("Category deleted successfully."))
        return redirect("courses:manage_categories")
    return render(
        request,
        "courses/confirm_delete.html",
        {"object": category, "title": _("Delete Category")},
    )


@login_required
def student_dashboard(request):
    enrollments = Enrollment.objects.filter(user=request.user, is_active=True)

    # For each enrollment, calculate progress
    for enrollment in enrollments:
        course = enrollment.course
        total_lessons = Lesson.objects.filter(module__course=course).count()
        completed_lessons = LessonProgress.objects.filter(
            enrollment=enrollment, is_completed=True
        ).count()

        enrollment.progress_percentage = (
            int((completed_lessons / total_lessons) * 100) if total_lessons > 0 else 0
        )
        enrollment.completed_lessons = completed_lessons
        enrollment.total_lessons = total_lessons

    return render(
        request,
        "courses/student_dashboard.html",
        {"enrollments": enrollments},
    )
