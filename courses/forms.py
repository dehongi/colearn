from django import forms
from django.utils.translation import gettext_lazy as _
from .models import (
    Course,
    Module,
    Lesson,
    Suggestion,
    Category,
    LessonProgress,
    CourseReview,
)


class BootstrapModelForm(forms.ModelForm):
    """Base form that adds Bootstrap 5 classes to every field."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add Bootstrap classes to all fields
        for field_name, field in self.fields.items():
            # Skip file fields as they have special handling in Bootstrap
            if isinstance(field.widget, forms.ClearableFileInput):
                field.widget.attrs.update(
                    {
                        "class": "form-control-file",
                    }
                )
            elif isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs.update(
                    {
                        "class": "form-check-input",
                    }
                )
            elif isinstance(
                field.widget, (forms.RadioSelect, forms.CheckboxSelectMultiple)
            ):
                field.widget.attrs.update(
                    {
                        "class": "form-check-input",
                    }
                )
            else:
                field.widget.attrs.update(
                    {
                        "class": "form-control",
                        "placeholder": field.label or field_name.capitalize(),
                    }
                )

            # Add Select2 classes to select fields
            if isinstance(field.widget, forms.Select):
                field.widget.attrs.update(
                    {
                        "class": "form-select",
                    }
                )


class CourseForm(BootstrapModelForm):
    class Meta:
        model = Course
        fields = [
            "title",
            "description",
            "category",
            "thumbnail",
            "price",
            "difficulty",
            "is_published",
        ]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 4}),
            "thumbnail": forms.ClearableFileInput(attrs={"class": "form-control"}),
        }
        help_texts = {
            "is_published": _("Only published courses will be visible to students."),
            "thumbnail": _("Recommended size: 1280x720 pixels."),
            "description": _(
                "A detailed description of what students will learn in this course."
            ),
        }


class ModuleForm(BootstrapModelForm):
    class Meta:
        model = Module
        fields = ["title", "description", "order"]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 3}),
            "order": forms.NumberInput(attrs={"min": 0}),
        }
        help_texts = {
            "order": _("Modules are displayed in ascending order (0, 1, 2, ...)."),
        }


class LessonForm(BootstrapModelForm):
    class Meta:
        model = Lesson
        fields = ["title", "content_type", "content", "video_url", "order"]
        widgets = {
            "content": forms.Textarea(attrs={"rows": 10}),
            "video_url": forms.URLInput(
                attrs={"placeholder": "https://www.youtube.com/embed/..."}
            ),
            "order": forms.NumberInput(attrs={"min": 0}),
        }
        help_texts = {
            "content_type": _("Select the type of content for this lesson."),
            "video_url": _(
                "For YouTube videos, use the embed URL (e.g., https://www.youtube.com/embed/VIDEO_ID)."
            ),
            "order": _("Lessons are displayed in ascending order within a module."),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Show/hide video_url field based on content_type
        if self.instance.pk and self.instance.content_type != "video":
            self.fields["video_url"].widget = forms.HiddenInput()


class SuggestionForm(BootstrapModelForm):
    class Meta:
        model = Suggestion
        fields = ["content"]
        widgets = {
            "content": forms.Textarea(
                attrs={
                    "rows": 4,
                    "placeholder": _(
                        "Enter your suggestion for improving this lesson..."
                    ),
                }
            ),
        }


class SuggestionStatusForm(BootstrapModelForm):
    class Meta:
        model = Suggestion
        fields = ["status", "instructor_response"]
        widgets = {
            "instructor_response": forms.Textarea(
                attrs={
                    "rows": 3,
                    "placeholder": _("Provide feedback to the suggestion (optional)"),
                }
            ),
        }


class CategoryForm(BootstrapModelForm):
    class Meta:
        model = Category
        fields = ["name", "description"]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 3}),
        }
        help_texts = {
            "name": _("The category name will be used for filtering courses."),
            "description": _("A brief description of this category (optional)."),
        }


class LessonProgressForm(BootstrapModelForm):
    class Meta:
        model = LessonProgress
        fields = ["is_completed"]


class CourseReviewForm(BootstrapModelForm):
    class Meta:
        model = CourseReview
        fields = ["rating", "review_text"]
        widgets = {
            "review_text": forms.Textarea(
                attrs={
                    "rows": 4,
                    "placeholder": _("Write your review of this course..."),
                }
            ),
            "rating": forms.NumberInput(
                attrs={"min": 1, "max": 5, "class": "form-range"}
            ),
        }
        help_texts = {
            "rating": _("Rate this course from 1 to 5 stars."),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Create a radio button select for ratings instead of number input
        self.fields["rating"].widget = forms.RadioSelect(
            choices=[(i, i) for i in range(1, 6)], attrs={"class": "rating-input"}
        )
