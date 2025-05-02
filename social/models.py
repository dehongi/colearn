from django.db import models
from django.urls import reverse
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.utils.text import slugify
from courses.models import Course, Lesson
from django.utils.functional import cached_property


class Discussion(models.Model):
    class Status(models.TextChoices):
        OPEN = "OPEN", _("Open")
        CLOSED = "CLOSED", _("Closed")
        ARCHIVED = "ARCHIVED", _("Archived")

    title = models.CharField(_("Title"), max_length=200)
    slug = models.SlugField(_("Slug"), unique=True, blank=True)
    content = models.TextField(_("Content"))
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="discussions",
    )
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name="discussions",
        null=True,
        blank=True,
    )
    lesson = models.ForeignKey(
        Lesson,
        on_delete=models.CASCADE,
        related_name="discussions",
        null=True,
        blank=True,
    )
    status = models.CharField(
        _("Status"),
        max_length=10,
        choices=Status.choices,
        default=Status.OPEN,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_pinned = models.BooleanField(_("Pinned"), default=False)
    is_announcement = models.BooleanField(_("Announcement"), default=False)
    views_count = models.PositiveIntegerField(_("Views"), default=0)

    class Meta:
        ordering = ["-is_pinned", "-is_announcement", "-created_at"]
        verbose_name = _("Discussion")
        verbose_name_plural = _("Discussions")
        indexes = [
            models.Index(fields=["slug"]),
            models.Index(fields=["status"]),
            models.Index(fields=["is_pinned", "is_announcement", "created_at"]),
        ]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
            # Ensure uniqueness
            counter = 1
            original_slug = self.slug
            while Discussion.objects.filter(slug=self.slug).exists():
                self.slug = f"{original_slug}-{counter}"
                counter += 1
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("social:discussion_detail", kwargs={"slug": self.slug})

    @cached_property
    def comment_count(self):
        return self.comments.count()

    @cached_property
    def solution_exists(self):
        return self.comments.filter(is_solution=True).exists()

    def increment_view_count(self):
        self.views_count += 1
        self.save(update_fields=["views_count"])

    def close(self):
        self.status = self.Status.CLOSED
        self.save(update_fields=["status"])

    def reopen(self):
        self.status = self.Status.OPEN
        self.save(update_fields=["status"])

    def archive(self):
        self.status = self.Status.ARCHIVED
        self.save(update_fields=["status"])


class Comment(models.Model):
    discussion = models.ForeignKey(
        Discussion,
        on_delete=models.CASCADE,
        related_name="comments",
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="comments",
    )
    content = models.TextField(_("Content"))
    parent = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        related_name="replies",
        null=True,
        blank=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_solution = models.BooleanField(_("Solution"), default=False)

    class Meta:
        ordering = ["created_at"]
        verbose_name = _("Comment")
        verbose_name_plural = _("Comments")
        indexes = [
            models.Index(fields=["is_solution"]),
            models.Index(fields=["created_at"]),
        ]

    def __str__(self):
        if len(self.content) > 50:
            return f"{self.content[:47]}..."
        return self.content

    @property
    def reply_count(self):
        return self.replies.count()

    @property
    def reaction_count(self):
        return self.reactions.count()

    def mark_as_solution(self):
        # Unmark any existing solution for this discussion
        Comment.objects.filter(discussion=self.discussion, is_solution=True).update(
            is_solution=False
        )
        # Mark this comment as the solution
        self.is_solution = True
        self.save(update_fields=["is_solution"])
        return True


class Reaction(models.Model):
    class Type(models.TextChoices):
        LIKE = "LIKE", _("Like")
        HELPFUL = "HELPFUL", _("Helpful")
        CONFUSED = "CONFUSED", _("Confused")
        THANKS = "THANKS", _("Thanks")
        INSIGHTFUL = "INSIGHTFUL", _("Insightful")

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="reactions",
    )
    comment = models.ForeignKey(
        Comment,
        on_delete=models.CASCADE,
        related_name="reactions",
    )
    type = models.CharField(
        _("Type"),
        max_length=15,
        choices=Type.choices,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ["user", "comment"]
        verbose_name = _("Reaction")
        verbose_name_plural = _("Reactions")
        indexes = [
            models.Index(fields=["type"]),
        ]

    def __str__(self):
        return f"{self.user.username} {self.get_type_display()} on {self.comment}"


class UserActivity(models.Model):
    class ActivityType(models.TextChoices):
        DISCUSSION_CREATED = "DISCUSSION_CREATED", _("Discussion Created")
        COMMENT_ADDED = "COMMENT_ADDED", _("Comment Added")
        REACTION_ADDED = "REACTION_ADDED", _("Reaction Added")
        SOLUTION_MARKED = "SOLUTION_MARKED", _("Solution Marked")
        DISCUSSION_VIEWED = "DISCUSSION_VIEWED", _("Discussion Viewed")
        DISCUSSION_CLOSED = "DISCUSSION_CLOSED", _("Discussion Closed")
        DISCUSSION_REOPENED = "DISCUSSION_REOPENED", _("Discussion Reopened")

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="activities",
    )
    activity_type = models.CharField(
        _("Activity Type"),
        max_length=20,
        choices=ActivityType.choices,
    )
    discussion = models.ForeignKey(
        Discussion,
        on_delete=models.CASCADE,
        related_name="activities",
        null=True,
        blank=True,
    )
    comment = models.ForeignKey(
        Comment,
        on_delete=models.CASCADE,
        related_name="activities",
        null=True,
        blank=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    additional_data = models.JSONField(_("Additional Data"), blank=True, null=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = _("User Activity")
        verbose_name_plural = _("User Activities")
        indexes = [
            models.Index(fields=["activity_type"]),
            models.Index(fields=["created_at"]),
        ]

    def __str__(self):
        return f"{self.user.username} {self.get_activity_type_display()}"

    @classmethod
    def log_activity(
        cls, user, activity_type, discussion=None, comment=None, additional_data=None
    ):
        """Utility method to create activity entries"""
        return cls.objects.create(
            user=user,
            activity_type=activity_type,
            discussion=discussion,
            comment=comment,
            additional_data=additional_data,
        )
