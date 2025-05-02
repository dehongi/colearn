from django.contrib import admin
from .models import Discussion, Comment, Reaction, UserActivity


@admin.register(Discussion)
class DiscussionAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "author",
        "course",
        "status",
        "is_pinned",
        "is_announcement",
        "created_at",
    )
    list_filter = ("status", "is_pinned", "is_announcement", "created_at")
    search_fields = ("title", "content", "author__username", "author__email")
    prepopulated_fields = {"slug": ("title",)}
    date_hierarchy = "created_at"


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = (
        "__str__",
        "author",
        "discussion",
        "parent",
        "is_solution",
        "created_at",
    )
    list_filter = ("is_solution", "created_at")
    search_fields = (
        "content",
        "author__username",
        "author__email",
        "discussion__title",
    )
    date_hierarchy = "created_at"


@admin.register(Reaction)
class ReactionAdmin(admin.ModelAdmin):
    list_display = ("user", "comment", "type", "created_at")
    list_filter = ("type", "created_at")
    search_fields = ("user__username", "user__email", "comment__content")


@admin.register(UserActivity)
class UserActivityAdmin(admin.ModelAdmin):
    list_display = ("user", "activity_type", "discussion", "comment", "created_at")
    list_filter = ("activity_type", "created_at")
    search_fields = ("user__username", "user__email", "discussion__title")
    date_hierarchy = "created_at"
