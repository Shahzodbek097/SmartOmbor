from django.db import models


class Category(models.Model):
    company = models.ForeignKey(
        "companies.Company",
        on_delete=models.PROTECT,
        related_name="categories",
        null=True,
        blank=True,
        verbose_name="Kompaniya"
    )
    nomi=models.CharField(max_length=100)
    description=models.TextField(blank=True)
    created_at=models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["company", "nomi"],
                name="unique_category_name_per_company"
            )
        ]

    def __str__(self):
        return self.nomi

class Product(models.Model):
    company = models.ForeignKey(
        "companies.Company",
        on_delete=models.PROTECT,
        related_name="products",
        null=True,
        blank=True,
        verbose_name="Kompaniya"
    )
    nomi=models.CharField(max_length=100)
    category=models.ForeignKey(Category, on_delete=models.PROTECT, related_name='products')
    xarid_narxi=models.DecimalField(max_digits=10, decimal_places=2)
    sotish_narxi=models.DecimalField(max_digits=10, decimal_places=2)
    qoldiq=models.PositiveIntegerField(default=0)
    min_qoldiq=models.PositiveIntegerField(default=10)
    created_at=models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nomi












