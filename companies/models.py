from django.db import models
from django.conf import settings


class Company(models.Model):
    nomi = models.CharField(
        max_length=200,
        verbose_name="Kompaniya nomi"
    )
    manzil = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="Manzil"
    )
    telefon = models.CharField(
        max_length=20,
        blank=True,
        verbose_name="Telefon"
    )
    email = models.EmailField(
        blank=True,
        verbose_name="Elektron pochta"
    )
    faol = models.BooleanField(
        default=True,
        verbose_name="Faol"
    )
    yaratilgan_vaqt = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        verbose_name = "Kompaniya"
        verbose_name_plural = "Kompaniyalar"

    def __str__(self):
        return self.nomi


class CompanyMembership(models.Model):

    class Role(models.TextChoices):
        RAHBAR = "Rahbar", "Rahbar"
        OMBORCHI = "Omborchi", "Omborchi"
        SOTUVCHI = "Sotuvchi", "Sotuvchi"

    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name="members"
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="company_memberships"
    )
    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.SOTUVCHI
    )
    faol = models.BooleanField(default=True)
    yaratilgan_vaqt = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        verbose_name = "Kompaniya a'zoligi"
        verbose_name_plural = "Kompaniya a'zoliklari"
        constraints = [
            models.UniqueConstraint(
                fields=["company", "user"],
                name="unique_company_user"
            )
        ]

    def __str__(self):
        return f"{self.user.username} - {self.company.nomi} ({self.role})"

