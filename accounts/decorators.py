from django.core.exceptions import PermissionDenied
from functools import wraps
from django.shortcuts import redirect
from companies.models import CompanyMembership


def role_required(*roles):
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            user = request.user

            if not user.is_authenticated:
                return redirect("accounts:login")

            if user.is_superuser:
                return view_func(request, *args, **kwargs)

            membership = CompanyMembership.objects.filter(
                user=user,
                faol=True,
                company__faol=True
            ).first()

            if membership and membership.role in roles:
                return view_func(request, *args, **kwargs)

            raise PermissionDenied

        return wrapper
    return decorator



def permission_required(permission):
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):

            if not request.user.is_authenticated:
                raise PermissionDenied

            if request.user.is_superuser:
                return view_func(request, *args, **kwargs)

            faol_azolik = CompanyMembership.objects.filter(
                user=request.user,
                faol=True,
                company__faol=True,
            ).exists()

            if faol_azolik and request.user.has_perm(permission):
                return view_func(request, *args, **kwargs)

            raise PermissionDenied

        return wrapper
    return decorator
