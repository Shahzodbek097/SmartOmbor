from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from products.models import Product
from django.db import transaction
from django.db.models import Max
from companies.models import Company


class Order(models.Model):

    class Status(models.TextChoices):
        PENDING = "PENDING", "Kutilmoqda"
        COMPLETED = "COMPLETED", "Yakunlangan"
        CANCELLED = "CANCELLED", "Bekor qilingan"

    company = models.ForeignKey(
        "companies.Company",
        on_delete=models.PROTECT,
        related_name="orders",
        null=True,
        blank=True,
        verbose_name="Kompaniya"
    )
    buyurtma_raqami = models.PositiveIntegerField(
        null=True,
        blank=True,
        editable=False,
        verbose_name="Buyurtma raqami"
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["company", "buyurtma_raqami"],
                name="unique_order_number_per_company"
            )
        ]

    customer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT,related_name="orders")
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    total_price = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.company_id:
            raise ValidationError(
                "Buyurtmaga kompaniya biriktirilishi shart!"
            )

        if self.pk is None and self.buyurtma_raqami is None:
            with transaction.atomic():

                Company.objects.select_for_update().get(pk=self.company_id)

                oxirgi_raqam = Order.objects.filter(
                    company_id=self.company_id
                ).aggregate(
                    max_raqam=Max("buyurtma_raqami")
                )["max_raqam"] or 0

                self.buyurtma_raqami = oxirgi_raqam + 1

                super().save(*args, **kwargs)
        else:
            super().save(*args, **kwargs)



class OrderItem(models.Model):

    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name="order_items")
    soni = models.PositiveIntegerField()
    narxi = models.DecimalField(max_digits=10, decimal_places=2)

    def save(self, *args, **kwargs):
        buyurtma = self.order
        mahsulot = self.product

        if not buyurtma.company_id:
            raise ValidationError(
                "Buyurtmaga kompaniya biriktirilmagan!"
            )

        if not mahsulot.company_id:
            raise ValidationError(
                "Mahsulot hech qanday kompaniyaga biriktirilmagan!"
            )

        if buyurtma.company_id != mahsulot.company_id:
            raise ValidationError(
                "Buyurtma va mahsulot boshqa-boshqa kompaniyalarga tegishli!"
            )

        if self.soni <= 0:
            raise ValidationError(
                "Mahsulot miqdori 0 dan katta bo‘lishi kerak!"
            )

        super().save(*args, **kwargs)

    @property
    def subtotal(self):
        return self.soni * self.narxi

    def __str__(self):
        return f"{self.product.nomi} - {self.soni} dona"

