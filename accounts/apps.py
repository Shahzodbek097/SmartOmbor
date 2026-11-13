from django.apps import AppConfig, apps


class AccountsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "accounts"

    def ready(self):
        from django.db.models.signals import post_migrate
        from .role_permissions import configure_role_permissions

        # API ilovasi INSTALLED_APPS ro'yxatida oxirida turadi.
        # Uning post_migrate signali barcha ilovalar ruxsatlari yaratilgach ishlaydi.
        post_migrate.connect(
            configure_role_permissions,
            sender=apps.get_app_config("api"),
            dispatch_uid="accounts.configure_role_permissions",
            weak=False,
        )
