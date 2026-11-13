from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.test import TestCase

from companies.models import Company, CompanyMembership
from .role_permissions import (
    ROLE_PERMISSIONS,
    assign_user_role,
    configure_role_permissions,
)


User = get_user_model()


class RolePermissionTests(TestCase):
    def setUp(self):
        configure_role_permissions()

    def test_all_role_groups_have_expected_permissions(self):
        for role, expected in ROLE_PERMISSIONS.items():
            with self.subTest(role=role):
                group = Group.objects.get(name=role)
                actual = set(
                    group.permissions.values_list(
                        "content_type__app_label",
                        "codename",
                    )
                )
                self.assertEqual(actual, set(expected))

    def test_role_assignment_replaces_previous_smartombor_role(self):
        user = User.objects.create_user(
            username="role-test-user",
            password="Test-password-123!",
        )
        company = Company.objects.create(nomi="Sinov kompaniyasi")
        CompanyMembership.objects.create(
            company=company,
            user=user,
            role=CompanyMembership.Role.SOTUVCHI,
            faol=True,
        )

        assign_user_role(user, CompanyMembership.Role.SOTUVCHI)
        self.assertTrue(user.groups.filter(name="Sotuvchi").exists())
        self.assertTrue(user.has_perm("sales.view_order"))
        self.assertTrue(user.has_perm("sales.add_order"))

        assign_user_role(user, CompanyMembership.Role.OMBORCHI)
        self.assertTrue(user.groups.filter(name="Omborchi").exists())
        self.assertFalse(user.groups.filter(name="Sotuvchi").exists())
        self.assertTrue(user.has_perm("inventory.view_ombormovement"))
        self.assertTrue(user.has_perm("products.view_product"))
        self.assertFalse(user.has_perm("sales.add_order"))

    def test_migration_setup_syncs_existing_memberships(self):
        user = User.objects.create_user(
            username="existing-role-user",
            password="Test-password-123!",
        )
        company = Company.objects.create(nomi="Mavjud kompaniya")
        CompanyMembership.objects.create(
            company=company,
            user=user,
            role=CompanyMembership.Role.RAHBAR,
            faol=True,
        )

        configure_role_permissions()

        self.assertTrue(user.groups.filter(name="Rahbar").exists())
        self.assertTrue(user.has_perm("products.view_product"))
        self.assertTrue(user.has_perm("sales.view_order"))
