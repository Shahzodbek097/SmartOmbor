from django import forms
from django.forms import formset_factory

from products.models import Product


class OrderItemForm(forms.Form):
    product = forms.ModelChoiceField(
        queryset=Product.objects.none(),
        label="Mahsulot",
    )

    soni = forms.IntegerField(
        min_value=1,
        label="Miqdori",
    )

    def __init__(self, *args, company=None, **kwargs):
        super().__init__(*args, **kwargs)

        if company:
            self.fields["product"].queryset = Product.objects.filter(
                company=company
            ).order_by("nomi")


OrderItemFormSet = formset_factory(
    OrderItemForm,
    extra=3,
    min_num=1,
    validate_min=True,
    can_delete=True,
)

