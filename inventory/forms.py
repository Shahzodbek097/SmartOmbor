from django import forms
from .models import OmborMovement


class OmborMovementForm(forms.ModelForm):
    class Meta:
        model = OmborMovement
        fields = [
            "product",
            "movement_type",
            "nechta",
            "sababi",
        ]

        labels = {
            "product": "Mahsulot",
            "movement_type": "Harakat turi",
            "nechta": "Miqdori",
            "sababi": "Sababi",
        }

        widgets = {
            "sababi": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Masalan: Yangi mahsulot keldi",
                }
            ),
        }
