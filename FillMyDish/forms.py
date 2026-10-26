from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from .models import Profile


class RegisterForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            "class": "form-input",
            "placeholder": "Change Your Email",
        }),
        label="Email",
    )
    full_name = forms.CharField(
        max_length=255,
        required=True,
        widget=forms.TextInput(attrs={
            "class": "form-input",
            "placeholder": "Change Your Full Name",
        }),
        label="Full Name",
    )
    username = forms.CharField(
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={
            "class": "form-input",
            "placeholder": "Change Your Username",
        }),
        label="Username",
    )

    class Meta:
        model = User
        fields = ["username", "email", "full_name", "password1", "password2"]

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


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ["full_name", "username", "email", "date_of_birth", "bio"]
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
        }
        labels = {
            "full_name": "Full Name",
            "username": "Username",
            "email": "Email",
            "date_of_birth": "Date of Birth",
            "bio": "Bio",
        }
