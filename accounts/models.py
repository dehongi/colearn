from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    class Role(models.TextChoices):
        INSTRUCTOR = "INSTRUCTOR", _("Instructor")
        LEARNER = "LEARNER", _("Learner")

    role = models.CharField(
        max_length=10,
        choices=Role.choices,
        default=Role.LEARNER,
        help_text=_("User role in the platform"),
    )
    bio = models.TextField(
        max_length=500, blank=True, help_text=_("User biography or description")
    )
    profile_picture = models.ImageField(
        upload_to="profile_pictures/",
        blank=True,
        null=True,
        help_text=_("User profile picture"),
    )
    date_of_birth = models.DateField(
        blank=True, null=True, help_text=_("User date of birth")
    )
    location = models.CharField(
        max_length=100, blank=True, help_text=_("User location")
    )
    website = models.URLField(
        max_length=200, blank=True, help_text=_("User website or portfolio")
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("user")
        verbose_name_plural = _("users")

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"

    @property
    def is_instructor(self):
        return self.role == self.Role.INSTRUCTOR

    @property
    def is_learner(self):
        return self.role == self.Role.LEARNER
