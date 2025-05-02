from django.contrib import admin
from .models import (
    Category,
    Course,
    Module,
    Lesson,
    Suggestion,
    Enrollment,
    LessonProgress,
    CourseReview,
)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ["name", "slug"]
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ["name"]


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = [
        "title",
        "instructor",
        "category",
        "price",
        "difficulty",
        "is_published",
        "created_at",
    ]
    list_filter = ["is_published", "difficulty", "category", "created_at"]
    search_fields = ["title", "description"]
    prepopulated_fields = {"slug": ("title",)}
    date_hierarchy = "created_at"


@admin.register(Module)
class ModuleAdmin(admin.ModelAdmin):
    list_display = ["title", "course", "order", "created_at"]
    list_filter = ["course"]
    search_fields = ["title", "description"]
    raw_id_fields = ["course"]


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ["title", "module", "content_type", "order", "created_at"]
    list_filter = ["content_type", "module__course"]
    search_fields = ["title", "content"]
    raw_id_fields = ["module"]


@admin.register(Suggestion)
class SuggestionAdmin(admin.ModelAdmin):
    list_display = ["user", "lesson", "status", "created_at"]
    list_filter = ["status", "created_at"]
    search_fields = ["content"]
    raw_id_fields = ["lesson", "user"]


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ["user", "course", "enrolled_at", "is_active"]
    list_filter = ["is_active", "enrolled_at"]
    search_fields = ["user__username", "course__title"]
    raw_id_fields = ["user", "course"]


@admin.register(LessonProgress)
class LessonProgressAdmin(admin.ModelAdmin):
    list_display = [
        "enrollment",
        "lesson",
        "is_completed",
        "last_accessed",
        "completed_at",
    ]
    list_filter = ["is_completed", "last_accessed", "completed_at"]
    raw_id_fields = ["enrollment", "lesson"]


@admin.register(CourseReview)
class CourseReviewAdmin(admin.ModelAdmin):
    list_display = ["enrollment", "rating", "created_at"]
    list_filter = ["rating", "created_at"]
    search_fields = ["review_text"]
    raw_id_fields = ["enrollment"]
