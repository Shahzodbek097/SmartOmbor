"""
SmartOmbor foydalanuvchi rollari uchun avtomatik Django Group ruxsatlari.
"""

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission


ROLE_PERMISSIONS = {
    "Rahbar": [
        ("products", "view_product"),
        ("products", "add_product"),
        ("products", "change_product"),
        ("products", "view_category"),
        ("products", "add_category"),
        ("products", "change_category"),
        ("sales", "view_order"),
    ],
    "Omborchi": [
        ("products", "view_product"),
        ("products", "add_product"),
        ("products", "change_product"),
        ("products", "view_category"),
        ("products", "add_category"),
        ("products", "change_category"),
        ("inventory", "view_ombormovement"),
        ("inventory", "add_ombormovement"),
    ],
    "Sotuvchi": [
        ("sales", "view_order"),
        ("sales", "add_order"),
    ],
}


def _permissions_for_role(role):
    """Rol uchun kerakli Permission obyektlarini topadi."""
    permissions = []
    missing = []

    for app_label, codename in ROLE_PERMISSIONS[role]:
        permission = Permission.objects.filter(
            content_type__app_label=app_label,
            codename=codename,
        ).first()

        if permission is None:
            missing.append(f"{app_label}.{codename}")
        else:
            permissions.append(permission)

    if missing:
        raise RuntimeError(
            "Rol ruxsatlari topilmadi: " + ", ".join(missing)
        )

    return permissions


def configure_role_permissions(sender=None, **kwargs):
    """
    migrate tugagandan keyin rol guruhlari va ruxsatlarini yaratadi.
    Mavjud faol kompaniya a'zolarini ham CompanyMembership.role
    qiymatiga qarab guruhlariga biriktiradi.
    """
    role_groups = {}

    for role in ROLE_PERMISSIONS:
        group, _ = Group.objects.get_or_create(name=role)
        group.permissions.set(_permissions_for_role(role))
        role_groups[role] = group

    User = get_user_model()
    from companies.models import CompanyMembership

    # Eski yoki noto'g'ri rol guruhlarini a'zolardan olib tashlaymiz.
    memberships_users = User.objects.filter(
        company_memberships__isnull=False
    ).distinct()

    role_group_list = list(role_groups.values())
    for user in memberships_users.iterator():
        user.groups.remove(*role_group_list)

    # Bitta user bir nechta kompaniyada bo'lsa, birinchi faol a'zolik
    # uning joriy kompaniyasi sifatida ishlatiladi (get_user_company bilan mos).
    memberships = (
        CompanyMembership.objects
        .filter(faol=True, company__faol=True)
        .select_related("user")
        .order_by("user_id", "id")
    )

    processed_user_ids = set()
    for membership in memberships.iterator():
        if membership.user_id in processed_user_ids:
            continue

        group = role_groups.get(membership.role)
        if group is not None:
            membership.user.groups.add(group)
            processed_user_ids.add(membership.user_id)


def assign_user_role(user, role):
    """
    Foydalanuvchiga SmartOmbor'dagi bitta rol guruhini biriktiradi.
    SmartOmbor'ning oldingi rol guruhini almashtiradi, boshqa guruhlarni
    esa saqlab qoladi.
    """
    if role not in ROLE_PERMISSIONS:
        raise ValueError(f"Noma'lum foydalanuvchi roli: {role}")

    group, _ = Group.objects.get_or_create(name=role)
    group.permissions.set(_permissions_for_role(role))

    old_role_groups = Group.objects.filter(
        name__in=ROLE_PERMISSIONS.keys()
    ).exclude(pk=group.pk)

    user.groups.remove(*old_role_groups)
    user.groups.add(group)

    # Django foydalanuvchi obyektida ruxsatlarni cache qiladi.
    # Rol o'zgargach shu obyekt qayta ishlatilsa, eski cache qolmasin.
    for cache_name in ("_perm_cache", "_user_perm_cache", "_group_perm_cache"):
        if hasattr(user, cache_name):
            delattr(user, cache_name)

    return group


def remove_smartombor_roles(user):
    """Foydalanuvchidan SmartOmbor rol guruhlarini olib tashlaydi."""
    old_role_groups = Group.objects.filter(name__in=ROLE_PERMISSIONS.keys())
    user.groups.remove(*old_role_groups)
