from django import forms
from django.contrib.auth.models import User, Group
from django.contrib.auth.forms import UserCreationForm


class UserCreateForm(UserCreationForm):
    first_name = forms.CharField(
        max_length=150,
        label="Ism",
        required=True,
    )

    last_name = forms.CharField(
        max_length=150,
        label="Familiya",
        required=True,
    )

    email = forms.EmailField(
        label="Elektron pochta",
        required=False,
    )

    role = forms.ModelChoiceField(
        queryset=Group.objects.filter(
            name__in=["Omborchi", "Sotuvchi", "Rahbar"]
        ),
        label="Foydalanuvchi roli",
        empty_label="Rolni tanlang",
    )

    class Meta:
        model = User
        fields = [
            "username",
            "first_name",
            "last_name",
            "email",
            "password1",
            "password2",
        ]
        labels = {
            "username": "Login",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field in self.fields.values():
            field.widget.attrs.update({
                "class": "form-control"
            })


class UserUpdateForm(forms.ModelForm):
    role = forms.ModelChoiceField(
        queryset=Group.objects.filter(
            name__in=["Omborchi", "Sotuvchi", "Rahbar"]
        ),
        label="Foydalanuvchi roli",
        required=True,
    )

    class Meta:
        model = User
        fields = [
            "username",
            "first_name",
            "last_name",
            "email",
            "is_active",
        ]
        labels = {
            "username": "Login",
            "first_name": "Ism",
            "last_name": "Familiya",
            "email": "Elektron pochta",
            "is_active": "Faol",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field in self.fields.values():
            field.widget.attrs.update({
                "class": "form-control"
            })

class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["first_name", "last_name", "email"]
        labels = {
            "first_name": "Ism",
            "last_name": "Familiya",
            "email": "Elektron pochta",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field in self.fields.values():
            field.widget.attrs.update({
                "class": "form-control"
            })