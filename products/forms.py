from django import forms
from .models import Product, Category


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = [
            "nomi",
            "category",
            "xarid_narxi",
            "sotish_narxi",
            "min_qoldiq",
        ]

        labels = {
            "nomi": "Mahsulot nomi",
            "category": "Kategoriya",
            "xarid_narxi": "Xarid narxi",
            "sotish_narxi": "Sotish narxi",
            "min_qoldiq": "Minimal qoldiq",
        }

        widgets = {
            "nomi": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Mahsulot nomini kiriting",
            }),
            "category": forms.Select(attrs={
                "class": "form-select",
            }),
            "xarid_narxi": forms.NumberInput(attrs={
                "class": "form-control",
                "step": "0.01",
            }),
            "sotish_narxi": forms.NumberInput(attrs={
                "class": "form-control",
                "step": "0.01",
            }),
            "min_qoldiq": forms.NumberInput(attrs={
                "class": "form-control",
            }),
        }

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ["nomi", "description"]

        labels = {
            "nomi": "Kategoriya nomi",
            "description": "Izoh",
        }

        widgets = {
            "nomi": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Masalan: Telefonlar",
            }),
            "description": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 3,
                "placeholder": "Kategoriya haqida ma'lumot",
            }),
        }