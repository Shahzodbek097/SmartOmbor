from django.contrib import admin
from .models import OmborMovement


@admin.register(OmborMovement)
class OmborMovementAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "company",
        "product",
        "user",
        "movement_type",
        "nechta",
        "sababi",
        "created_at",
    )

    list_filter = (
        "company",
        "movement_type",
        "created_at",
        "user",
    )

    search_fields = (
        "company__nomi",
        "product__nomi",
        "user__username",
        "sababi",
    )

    readonly_fields = ("created_at",)

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False