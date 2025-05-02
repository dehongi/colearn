from django import forms
from django.contrib.auth.forms import (
    UserCreationForm,
    AuthenticationForm,
    PasswordChangeForm,
    PasswordResetForm,
    SetPasswordForm,
)
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import authenticate
from .models import User


class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(
        widget=forms.EmailInput(
            attrs={"class": "form-control", "placeholder": _("Email address")}
        )
    )
    username = forms.CharField(
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": _("Username")}
        )
    )
    first_name = forms.CharField(
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": _("First name")}
        )
    )
    last_name = forms.CharField(
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": _("Last name")}
        )
    )
    password1 = forms.CharField(
        label=_("Password"),
        widget=forms.PasswordInput(
            attrs={"class": "form-control", "placeholder": _("Password")}
        ),
    )
    password2 = forms.CharField(
        label=_("Confirm Password"),
        widget=forms.PasswordInput(
            attrs={"class": "form-control", "placeholder": _("Confirm password")}
        ),
    )
    role = forms.ChoiceField(
        choices=User.Role.choices, widget=forms.Select(attrs={"class": "form-select"})
    )

    class Meta:
        model = User
        fields = (
            "username",
            "email",
            "first_name",
            "last_name",
            "password1",
            "password2",
            "role",
        )


class CustomAuthenticationForm(AuthenticationForm):
    username = forms.CharField(
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": _("Username or Email")}
        )
    )
    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={"class": "form-control", "placeholder": _("Password")}
        )
    )

    def clean(self):
        username = self.cleaned_data.get("username")
        password = self.cleaned_data.get("password")

        if username is not None and password:
            # Check if the provided username is an email
            if "@" in username:
                # Find the user with this email
                try:
                    user = User.objects.get(email=username)
                    # If found, use the username for authentication
                    username = user.username
                except User.DoesNotExist:
                    pass

            self.user_cache = authenticate(
                self.request, username=username, password=password
            )

            if self.user_cache is None:
                raise forms.ValidationError(
                    self.error_messages["invalid_login"],
                    code="invalid_login",
                    params={"username": self.username_field.verbose_name},
                )
            else:
                self.confirm_login_allowed(self.user_cache)

        return self.cleaned_data


class UserProfileForm(forms.ModelForm):
    first_name = forms.CharField(
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": _("First name")}
        )
    )
    last_name = forms.CharField(
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": _("Last name")}
        )
    )
    email = forms.EmailField(
        widget=forms.EmailInput(
            attrs={"class": "form-control", "placeholder": _("Email address")}
        )
    )
    bio = forms.CharField(
        required=False,
        widget=forms.Textarea(
            attrs={
                "class": "form-control",
                "placeholder": _("Tell us about yourself"),
                "rows": 4,
            }
        ),
    )
    date_of_birth = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={"class": "form-control", "type": "date"}),
    )
    location = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": _("Your location")}
        ),
    )
    website = forms.URLField(
        required=False,
        widget=forms.URLInput(
            attrs={
                "class": "form-control",
                "placeholder": _("Your website or portfolio"),
            }
        ),
    )
    profile_picture = forms.ImageField(
        required=False, widget=forms.FileInput(attrs={"class": "form-control"})
    )

    class Meta:
        model = User
        fields = (
            "first_name",
            "last_name",
            "email",
            "bio",
            "date_of_birth",
            "location",
            "website",
            "profile_picture",
        )


class CustomPasswordChangeForm(PasswordChangeForm):
    old_password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={"class": "form-control", "placeholder": _("Current password")}
        ),
        label=_("Current password"),
    )
    new_password1 = forms.CharField(
        widget=forms.PasswordInput(
            attrs={"class": "form-control", "placeholder": _("New password")}
        ),
        label=_("New password"),
    )
    new_password2 = forms.CharField(
        widget=forms.PasswordInput(
            attrs={"class": "form-control", "placeholder": _("Confirm new password")}
        ),
        label=_("Confirm new password"),
    )


class CustomPasswordResetForm(PasswordResetForm):
    email = forms.EmailField(
        widget=forms.EmailInput(
            attrs={"class": "form-control", "placeholder": _("Email address")}
        ),
        label=_("Email address"),
    )


class CustomSetPasswordForm(SetPasswordForm):
    new_password1 = forms.CharField(
        widget=forms.PasswordInput(
            attrs={"class": "form-control", "placeholder": _("New password")}
        ),
        label=_("New password"),
    )
    new_password2 = forms.CharField(
        widget=forms.PasswordInput(
            attrs={"class": "form-control", "placeholder": _("Confirm new password")}
        ),
        label=_("Confirm new password"),
    )
