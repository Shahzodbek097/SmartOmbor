from django.contrib import admin
from .models import Company, CompanyMembership


class CompanyMembershipInline(admin.TabularInline):
    model = CompanyMembership
    extra = 1


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ("nomi", "telefon", "email", "faol", "yaratilgan_vaqt")
    search_fields = ("nomi", "telefon", "email")
    list_filter = ("faol",)
    inlines = [CompanyMembershipInline]


@admin.register(CompanyMembership)
class CompanyMembershipAdmin(admin.ModelAdmin):
    list_display = ("user", "company", "role", "faol")
    list_filter = ("company", "role", "faol")
    search_fields = ("user__username", "company__nomi")

