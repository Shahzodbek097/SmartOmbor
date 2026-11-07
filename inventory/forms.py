from django import forms
from .models import OmborMovement
from products.models import Product


class OmborMovementForm(forms.ModelForm):

    def __init__(self, *args, company=None, **kwargs):
        super().__init__(*args, **kwargs)

        if company:
            self.fields["product"].queryset = Product.objects.filter(
                company=company
            ).order_by("nomi")
        else:
            self.fields["product"].queryset = Product.objects.none()

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
