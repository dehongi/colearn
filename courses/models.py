from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.utils.text import slugify
from django.urls import reverse
from django.core.validators import MinValueValidator, MaxValueValidator


class Category(models.Model):
    name = models.CharField(_("Name"), max_length=100)
    slug = models.SlugField(_("Slug"), unique=True, blank=True)
    description = models.TextField(_("Description"), blank=True)

    class Meta:
        verbose_name = _("Category")
        verbose_name_plural = _("Categories")
        ordering = ["name"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Course(models.Model):
    DIFFICULTY_CHOICES = (
        ("beginner", _("Beginner")),
        ("intermediate", _("Intermediate")),
        ("advanced", _("Advanced")),
    )

    title = models.CharField(_("Title"), max_length=200)
    slug = models.SlugField(_("Slug"), unique=True, blank=True)
    description = models.TextField(_("Description"))
    instructor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="courses",
        limit_choices_to={"role": "INSTRUCTOR"},
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        related_name="courses",
        null=True,
        blank=True,
    )
    thumbnail = models.ImageField(_("Thumbnail"), upload_to="course_thumbnails/")
    price = models.DecimalField(
        _("Price"), max_digits=10, decimal_places=2, default=0.00
    )
    difficulty = models.CharField(
        _("Difficulty"), max_length=15, choices=DIFFICULTY_CHOICES, default="beginner"
    )
    is_published = models.BooleanField(_("Published"), default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = _("Course")
        verbose_name_plural = _("Courses")

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("courses:course_detail", kwargs={"slug": self.slug})


class Module(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="modules")
    title = models.CharField(_("Title"), max_length=200)
    description = models.TextField(_("Description"), blank=True)
    order = models.PositiveIntegerField(_("Order"), default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["order", "created_at"]
        verbose_name = _("Module")
        verbose_name_plural = _("Modules")

    def __str__(self):
        return f"{self.course.title} - {self.title}"


class Lesson(models.Model):
    CONTENT_TYPE_CHOICES = (
        ("text", _("Text")),
        ("video", _("Video")),
        ("quiz", _("Quiz")),
    )

    module = models.ForeignKey(Module, on_delete=models.CASCADE, related_name="lessons")
    title = models.CharField(_("Title"), max_length=200)
    content = models.TextField(_("Content"))
    content_type = models.CharField(
        _("Content Type"), max_length=10, choices=CONTENT_TYPE_CHOICES, default="text"
    )
    video_url = models.URLField(_("Video URL"), blank=True, null=True)
    order = models.PositiveIntegerField(_("Order"), default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["order", "created_at"]
        verbose_name = _("Lesson")
        verbose_name_plural = _("Lessons")

    def __str__(self):
        return f"{self.module.title} - {self.title}"


class Suggestion(models.Model):
    class Status(models.TextChoices):
        PENDING = "PENDING", _("Pending")
        APPROVED = "APPROVED", _("Approved")
        REJECTED = "REJECTED", _("Rejected")

    lesson = models.ForeignKey(
        Lesson, on_delete=models.CASCADE, related_name="suggestions"
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="suggestions"
    )
    content = models.TextField(_("Content"))
    instructor_response = models.TextField(
        _("Instructor Response"), blank=True, null=True
    )
    status = models.CharField(
        _("Status"), max_length=10, choices=Status.choices, default=Status.PENDING
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = _("Suggestion")
        verbose_name_plural = _("Suggestions")

    def __str__(self):
        return f"Suggestion by {self.user.username} for {self.lesson.title}"


class Enrollment(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="enrollments"
    )
    course = models.ForeignKey(
        Course, on_delete=models.CASCADE, related_name="enrollments"
    )
    enrolled_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(_("Active"), default=True)

    class Meta:
        unique_together = ["user", "course"]
        verbose_name = _("Enrollment")
        verbose_name_plural = _("Enrollments")

    def __str__(self):
        return f"{self.user.username} enrolled in {self.course.title}"


class LessonProgress(models.Model):
    enrollment = models.ForeignKey(
        Enrollment, on_delete=models.CASCADE, related_name="lesson_progress"
    )
    lesson = models.ForeignKey(
        Lesson, on_delete=models.CASCADE, related_name="progress_records"
    )
    is_completed = models.BooleanField(_("Completed"), default=False)
    last_accessed = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ["enrollment", "lesson"]
        verbose_name = _("Lesson Progress")
        verbose_name_plural = _("Lesson Progress Records")

    def __str__(self):
        return f"{self.enrollment.user.username}'s progress on {self.lesson.title}"


class CourseReview(models.Model):
    enrollment = models.OneToOneField(
        Enrollment, on_delete=models.CASCADE, related_name="review"
    )
    rating = models.PositiveSmallIntegerField(
        _("Rating"), validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    review_text = models.TextField(_("Review"), blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("Course Review")
        verbose_name_plural = _("Course Reviews")

    def __str__(self):
        return f"{self.enrollment.user.username}'s review of {self.enrollment.course.title}"
