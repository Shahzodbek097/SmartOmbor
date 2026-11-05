from django.db import models
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.models import User, Group
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.core.paginator import Paginator

from .decorators import role_required
from .forms import UserCreateForm, UserUpdateForm, ProfileUpdateForm


def get_available_roles(user):
    """Foydalanuvchiga berish mumkin bo'lgan rollar."""
    if user.is_superuser:
        return Group.objects.filter(
            name__in=["Omborchi", "Sotuvchi", "Rahbar"]
        )

    return Group.objects.filter(
        name__in=["Omborchi", "Sotuvchi"]
    )



@role_required("Rahbar")
def user_list(request):
    users = User.objects.all().order_by("-date_joined")

    if not request.user.is_superuser:
        users = users.filter(is_superuser=False)

    # Qidiruv
    qidiruv = request.GET.get("q", "")

    if qidiruv:
        users = users.filter(
            models.Q(username__icontains=qidiruv) |
            models.Q(first_name__icontains=qidiruv) |
            models.Q(last_name__icontains=qidiruv) |
            models.Q(email__icontains=qidiruv)
        )

    # Sahifalash
    paginator = Paginator(users, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(request, "accounts/user_list.html", {
        "users": page_obj,
        "page_obj": page_obj,
        "qidiruv": qidiruv,
    })



@role_required("Rahbar")
def user_create(request):
    form = UserCreateForm(request.POST or None)

    form.fields["role"].queryset = get_available_roles(request.user)

    if request.method == "POST" and form.is_valid():
        user = form.save()
        role = form.cleaned_data["role"]

        user.groups.set([role])

        messages.success(request, "Yangi foydalanuvchi muvaffaqiyatli qo'shildi.")
        return redirect("accounts:user_list")

    return render(request, "accounts/user_form.html", {
        "form": form,
        "title": "Yangi foydalanuvchi qo'shish",
    })


@role_required("Rahbar")
def user_update(request, user_id):
    user = get_object_or_404(User, id=user_id)

    if user.is_superuser and not request.user.is_superuser:
        messages.error(request, "Superuser ma'lumotlarini tahrirlash mumkin emas.")
        return redirect("accounts:user_list")

    form = UserUpdateForm(request.POST or None, instance=user)

    form.fields["role"].queryset = get_available_roles(request.user)

    if request.method == "GET":
        form.initial["role"] = user.groups.first()

    if request.method == "POST" and form.is_valid():
        user = form.save()
        role = form.cleaned_data["role"]

        user.groups.set([role])

        messages.success(request, "Foydalanuvchi ma'lumotlari yangilandi.")
        return redirect("accounts:user_list")

    return render(request, "accounts/user_form.html", {
        "form": form,
        "title": "Foydalanuvchini tahrirlash",
    })


@role_required("Rahbar")
@require_POST
def user_toggle_status(request, user_id):
    user = get_object_or_404(User, id=user_id)

    if user.is_superuser and not request.user.is_superuser:
        messages.error(request, "Superuser holatini o'zgartirish mumkin emas.")
        return redirect("accounts:user_list")

    if user == request.user:
        messages.error(request, "O'zingizning hisobingizni o'chira olmaysiz.")
        return redirect("accounts:user_list")

    user.is_active = not user.is_active
    user.save(update_fields=["is_active"])

    messages.success(request, "Foydalanuvchi holati o'zgartirildi.")
    return redirect("accounts:user_list")


@login_required
def profile(request):
    user = request.user

    role = user.groups.first()

    return render(request, "accounts/profile.html", {
        "profile_user": user,
        "role": role,
    })

@login_required
def profile_update(request):
    form = ProfileUpdateForm(
        request.POST or None,
        instance=request.user
    )

    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(
            request,
            "Shaxsiy ma'lumotlaringiz muvaffaqiyatli yangilandi."
        )
        return redirect("accounts:profile")

    return render(request, "accounts/profile_update.html", {
        "form": form,
    })