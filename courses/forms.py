from django import forms
from django.utils.translation import gettext_lazy as _
from .models import Course, Module, Lesson, Suggestion


class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ["title", "description", "thumbnail", "price", "is_published"]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 4}),
        }


class ModuleForm(forms.ModelForm):
    class Meta:
        model = Module
        fields = ["title", "description", "order"]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 3}),
        }


class LessonForm(forms.ModelForm):
    class Meta:
        model = Lesson
        fields = ["title", "content", "order"]
        widgets = {
            "content": forms.Textarea(attrs={"rows": 10}),
        }


class SuggestionForm(forms.ModelForm):
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


class SuggestionStatusForm(forms.ModelForm):
    class Meta:
        model = Suggestion
        fields = ["status"]
        widgets = {
            "status": forms.Select(attrs={"class": "form-select"}),
        }
