from rest_framework.permissions import BasePermission

from companies.models import CompanyMembership
from companies.utils import get_user_company


class CompanyRolePermission(BasePermission):
    """
    Foydalanuvchining faol kompaniyasi va rolini tekshiradi.
    """

    message = "Sizda ushbu amalni bajarish uchun ruxsat yo'q."

    def has_permission(self, request, view):

        user = request.user

        if not user or not user.is_authenticated:
            return False

        company = get_user_company(user)

        if not company:
            return False

        if user.is_superuser:
            return True

        membership = CompanyMembership.objects.filter(
            user=user,
            company=company,
            faol=True,
            company__faol=True,
        ).first()

        if not membership:
            return False

        role_permissions = getattr(
            view,
            "role_permissions",
            {}
        )

        allowed_roles = role_permissions.get(
            getattr(view, "action", None)
        )

        if allowed_roles is None:
            return True

        return membership.role in allowed_roles



class DenyDjoserUserCreate(BasePermission):
    """
    Djoser orqali kompaniyasiz foydalanuvchi
    yaratishni taqiqlaydi.
    """

    def has_permission(self, request, view):
        return False

