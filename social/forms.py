from django import forms
from django.utils.translation import gettext_lazy as _
from .models import Discussion, Comment, Reaction, UserActivity


class DiscussionForm(forms.ModelForm):
    class Meta:
        model = Discussion
        fields = ["title", "content", "status", "is_pinned", "is_announcement"]
        widgets = {
            "title": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": _("Enter discussion title..."),
                }
            ),
            "content": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 5,
                    "placeholder": _("Write your discussion content here..."),
                }
            ),
            "status": forms.Select(
                attrs={"class": "form-select"},
            ),
            "is_pinned": forms.CheckboxInput(
                attrs={"class": "form-check-input"},
            ),
            "is_announcement": forms.CheckboxInput(
                attrs={"class": "form-check-input"},
            ),
        }


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ["content"]
        widgets = {
            "content": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "placeholder": _("Write your comment here..."),
                }
            ),
        }


class ReplyForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ["content"]
        widgets = {
            "content": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 2,
                    "placeholder": _("Write your reply here..."),
                }
            ),
        }


class ReactionForm(forms.ModelForm):
    class Meta:
        model = Reaction
        fields = ["type"]
        widgets = {
            "type": forms.Select(
                attrs={"class": "form-select"},
            ),
        }


class DiscussionFilterForm(forms.Form):
    STATUS_CHOICES = [
        ("", _("All Status")),
        ("OPEN", _("Open")),
        ("CLOSED", _("Closed")),
        ("ARCHIVED", _("Archived")),
    ]

    SORT_CHOICES = [
        ("-created_at", _("Newest First")),
        ("created_at", _("Oldest First")),
        ("-is_pinned", _("Pinned First")),
    ]

    status = forms.ChoiceField(
        choices=STATUS_CHOICES,
        required=False,
        widget=forms.Select(attrs={"class": "form-select"}),
    )
    sort = forms.ChoiceField(
        choices=SORT_CHOICES,
        required=False,
        widget=forms.Select(attrs={"class": "form-select"}),
    )
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": _("Search discussions..."),
            }
        ),
    )
    is_announcement = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={"class": "form-check-input"}),
    )
    is_solved = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={"class": "form-check-input"}),
    )


class ActivityFilterForm(forms.Form):
    ACTIVITY_TYPE_CHOICES = [
        ("", _("All Activities")),
    ] + UserActivity.ActivityType.choices

    SORT_CHOICES = [
        ("-created_at", _("Newest First")),
        ("created_at", _("Oldest First")),
    ]

    activity_type = forms.ChoiceField(
        choices=ACTIVITY_TYPE_CHOICES,
        required=False,
        label=_("Activity Type"),
        widget=forms.Select(attrs={"class": "form-select"}),
    )

    date_from = forms.DateField(
        required=False,
        label=_("From Date"),
        widget=forms.DateInput(attrs={"class": "form-control", "type": "date"}),
    )

    date_to = forms.DateField(
        required=False,
        label=_("To Date"),
        widget=forms.DateInput(attrs={"class": "form-control", "type": "date"}),
    )

    sort = forms.ChoiceField(
        choices=SORT_CHOICES,
        required=False,
        initial="-created_at",
        label=_("Sort By"),
        widget=forms.Select(attrs={"class": "form-select"}),
    )
