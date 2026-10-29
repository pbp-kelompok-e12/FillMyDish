from django import forms
from django.forms import inlineformset_factory
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from .models import Profile, Connection
from django.core.exceptions import ValidationError
from .models import Profile, Connection, User
from django.conf import settings

# forms.py -> mendefinisikan form untuk pendaftaran, login, pengeditan profil, dan koneksi media 
#             sosial. Formulir ini digunakan untuk memvalidasi input pengguna dan menyimpan data 
#             ke model terkait.

class RegisterForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            "class": "form-input",
            "placeholder": "Enter Your Email",
        }),
        label="Email",
    )
    full_name = forms.CharField(
        max_length=255,
        required=True,
        widget=forms.TextInput(attrs={
            "class": "form-input",
            "placeholder": "Enter Your Full Name",
        }),
        label="Full Name",
    )
    username = forms.CharField(
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={
            "class": "form-input",
            "placeholder": "Enter Your Username",
        }),
        label="Username",
    )
    moderator_key = forms.CharField(
        required=False,
        widget=forms.PasswordInput
    )
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "email", "full_name", "password1", "password2")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["password1"].widget.attrs.update({
            "class": "form-input",
            "placeholder": "Enter Your Password",
        })
        self.fields["password2"].widget.attrs.update({
            "class": "form-input",
            "placeholder": "Confirm Your Password",
        })
        self.fields["password1"].label = "Password"
        self.fields["password2"].label = "Confirm Password"

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        if self.cleaned_data["moderator_key"] == settings.MODERATOR_KEY:
            user.is_moderator = True
        else:
            user.is_moderator = False
        if commit:
            user.save()
            Profile.objects.create(
                user=user,
                username=user.username,
                full_name=self.cleaned_data["full_name"],
                email=self.cleaned_data["email"],
            )
        return user


class LoginForm(AuthenticationForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            "class": "form-input",
            "placeholder": "Enter Your Username",
        }),
        label="Username",
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            "class": "form-input",
            "placeholder": "Enter Your Password",
        }),
        label="Password",
    )
    def confirm_login_allowed(self, user):
        super().confirm_login_allowed(user)
        if user.is_banned:
            raise ValidationError(
                "This account has been banned.",
                code="banned",
            )


class ConnectionForm(forms.ModelForm):
    class Meta:
        model = Connection
        fields = ["platform", "url"]
        widgets = {
            "platform": forms.TextInput(attrs={
                "class": "form-input",
                "placeholder": "Platform (e.g. Instagram)",
            }),
            "url": forms.URLInput(attrs={
                "class": "form-input",
                "placeholder": "https://instagram.com/...",
            }),
        }
        labels = {
            "platform": "Platform",
            "url": "Link",
        }


# Bisa >1: mulai 1 baris kosong, tambah lebih banyak via tombol "+ Add Connection"
ConnectionFormSet = inlineformset_factory(
    Profile,
    Connection,
    form=ConnectionForm,
    fields=["platform", "url"],
    extra=1,
    can_delete=True,
)


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ["full_name", "username", "email", "date_of_birth", "bio", "profile_image"]
        widgets = {
            "full_name": forms.TextInput(attrs={
                "class": "form-input",
                "placeholder": "Change Your Full Name",
            }),
            "username": forms.TextInput(attrs={
                "class": "form-input",
                "placeholder": "Change Your Username",
            }),
            "email": forms.EmailInput(attrs={
                "class": "form-input",
                "placeholder": "Change Your Email",
            }),
            "date_of_birth": forms.DateInput(attrs={
                "class": "form-input",
                "placeholder": "YYYY-MM-DD",
                "type": "date",
            }),
            "bio": forms.Textarea(attrs={
                "class": "form-input form-textarea",
                "placeholder": "Change Your Bio",
                "rows": 3,
            }),
            "profile_image": forms.FileInput(attrs={"class": "form-input profile-image-input", "accept": "image/*"}),
        }
        labels = {
            "full_name": "Full Name",
            "username": "Username",
            "email": "Email",
            "date_of_birth": "Date of Birth",
            "bio": "Bio",
            "profile_image": "Profile Picture",
        }
