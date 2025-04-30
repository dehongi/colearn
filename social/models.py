from django.db import models
from django.urls import reverse
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.utils.text import slugify
from courses.models import Course, Lesson


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

    class Meta:
        ordering = ["-is_pinned", "-is_announcement", "-created_at"]
        verbose_name = _("Discussion")
        verbose_name_plural = _("Discussions")

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("social:discussion_detail", kwargs={"slug": self.slug})


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

    def __str__(self):
        return f"Comment by {self.author.username} on {self.discussion.title}"


class Reaction(models.Model):
    class Type(models.TextChoices):
        LIKE = "LIKE", _("Like")
        HELPFUL = "HELPFUL", _("Helpful")
        CONFUSED = "CONFUSED", _("Confused")

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
        max_length=10,
        choices=Type.choices,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ["user", "comment"]
        verbose_name = _("Reaction")
        verbose_name_plural = _("Reactions")

    def __str__(self):
        return f"{self.user.username} {self.get_type_display()} on {self.comment}"


class UserActivity(models.Model):
    class ActivityType(models.TextChoices):
        DISCUSSION_CREATED = "DISCUSSION_CREATED", _("Discussion Created")
        COMMENT_ADDED = "COMMENT_ADDED", _("Comment Added")
        REACTION_ADDED = "REACTION_ADDED", _("Reaction Added")
        SOLUTION_MARKED = "SOLUTION_MARKED", _("Solution Marked")

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

    class Meta:
        ordering = ["-created_at"]
        verbose_name = _("User Activity")
        verbose_name_plural = _("User Activities")

    def __str__(self):
        return f"{self.user.username} {self.get_activity_type_display()}"
