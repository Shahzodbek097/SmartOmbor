from django.db import models
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.models import User, Group
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.core.paginator import Paginator
from companies.models import CompanyMembership
from django.db import transaction
from django.contrib.auth import login

from .decorators import role_required
from .forms import UserCreateForm, UserUpdateForm, ProfileUpdateForm, RegisterForm
from companies.utils import get_user_company
from companies.models import Company


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
    company = get_user_company(request.user)

    if not company:
        messages.error(request, "Kompaniya topilmadi.")
        return redirect("accounts:profile")

    users = User.objects.filter(
        company_memberships__company=company
    ).distinct().order_by("-date_joined")

    if not request.user.is_superuser:
        users = users.filter(is_superuser=False)

    qidiruv = request.GET.get("q", "").strip()

    if qidiruv:
        users = users.filter(
            models.Q(username__icontains=qidiruv) |
            models.Q(first_name__icontains=qidiruv) |
            models.Q(last_name__icontains=qidiruv) |
            models.Q(email__icontains=qidiruv)
        )

    paginator = Paginator(users, 10)
    page_obj = paginator.get_page(request.GET.get("page"))

    return render(request, "accounts/user_list.html", {
        "users": page_obj,
        "page_obj": page_obj,
        "qidiruv": qidiruv,
    })


@role_required("Rahbar")
def user_create(request):
    company = get_user_company(request.user)

    if not company:
        messages.error(request, "Siz kompaniyaga biriktirilmagansiz.")
        return redirect("accounts:profile")

    form = UserCreateForm(request.POST or None)
    form.fields["role"].queryset = get_available_roles(request.user)

    if request.method == "POST" and form.is_valid():
        role = form.cleaned_data["role"]

        with transaction.atomic():
            user = form.save()

            CompanyMembership.objects.create(
                company=company,
                user=user,
                role=role.name,
                faol=True
            )

        messages.success(
            request,
            "Yangi foydalanuvchi muvaffaqiyatli qo'shildi."
        )
        return redirect("accounts:user_list")

    return render(request, "accounts/user_form.html", {
        "form": form,
        "title": "Yangi foydalanuvchi qo'shish",
    })


@role_required("Rahbar")
def user_update(request, user_id):
    company = get_user_company(request.user)

    if not company:
        messages.error(request, "Kompaniya topilmadi.")
        return redirect("accounts:user_list")

    user = get_object_or_404(
        User,
        id=user_id,
        company_memberships__company=company
    )

    membership = get_object_or_404(
        CompanyMembership,
        user=user,
        company=company
    )

    if user.is_superuser and not request.user.is_superuser:
        messages.error(
            request,
            "Superuser ma'lumotlarini tahrirlash mumkin emas."
        )
        return redirect("accounts:user_list")

    form = UserUpdateForm(
        request.POST or None,
        instance=user
    )

    form.fields["role"].queryset = get_available_roles(request.user)

    if request.method == "GET":
        form.initial["role"] = Group.objects.filter(
            name=membership.role
        ).first()

    if request.method == "POST" and form.is_valid():
        role = form.cleaned_data["role"]

        with transaction.atomic():
            form.save()

            membership.role = role.name
            membership.save(update_fields=["role"])

        messages.success(
            request,
            "Foydalanuvchi ma'lumotlari yangilandi."
        )
        return redirect("accounts:user_list")

    return render(request, "accounts/user_form.html", {
        "form": form,
        "title": "Foydalanuvchini tahrirlash",
    })


@role_required("Rahbar")
@require_POST
def user_toggle_status(request, user_id):
    company = get_user_company(request.user)

    if not company:
        messages.error(request, "Kompaniya topilmadi.")
        return redirect("accounts:user_list")

    user = get_object_or_404(
        User,
        id=user_id,
        company_memberships__company=company
    )

    membership = get_object_or_404(
        CompanyMembership,
        user=user,
        company=company
    )

    if user.is_superuser and not request.user.is_superuser:
        messages.error(
            request,
            "Superuser holatini o'zgartirish mumkin emas."
        )
        return redirect("accounts:user_list")

    if user == request.user:
        messages.error(
            request,
            "O'zingizning hisobingizni o'chira olmaysiz."
        )
        return redirect("accounts:user_list")

    membership.faol = not membership.faol
    membership.save(update_fields=["faol"])

    messages.success(
        request,
        "Foydalanuvchining kompaniyadagi holati o'zgartirildi."
    )
    return redirect("accounts:user_list")


@login_required
def profile(request):
    user = request.user
    company = get_user_company(user)

    membership = None
    role = None

    if company:
        membership = CompanyMembership.objects.filter(
            user=user,
            company=company,
            faol=True,
            company__faol=True
        ).first()

    if membership:
        role = Group.objects.filter(
            name=membership.role
        ).first()

    return render(request, "accounts/profile.html", {
        "profile_user": user,
        "role": role,
        "membership": membership,
        "company": company,
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


def register(request):
    if request.user.is_authenticated:
        return redirect("accounts:profile")

    form = RegisterForm(request.POST or None)

    if request.method == "POST" and form.is_valid():

        with transaction.atomic():
            # Foydalanuvchini yaratish
            user = form.save()

            # Yangi kompaniya yaratish
            company = Company.objects.create(
                nomi=form.cleaned_data["company_nomi"],
                manzil=form.cleaned_data["company_manzil"],
                telefon=form.cleaned_data["company_telefon"],
                email=form.cleaned_data["company_email"],
            )

            # Birinchi foydalanuvchini Rahbar qilish
            CompanyMembership.objects.create(
                company=company,
                user=user,
                role=CompanyMembership.Role.RAHBAR,
                faol=True
            )

            # Eski Group tizimi bilan moslik
            rahbar_group, _ = Group.objects.get_or_create(
                name="Rahbar"
            )
            user.groups.add(rahbar_group)

        # Ro'yxatdan o'tgandan so'ng avtomatik kirish
        login(request, user)

        messages.success(
            request,
            "Ro'yxatdan o'tish muvaffaqiyatli yakunlandi!"
        )

        return redirect("accounts:profile")

    return render(
        request,
        "accounts/register.html",
        {"form": form}
    )

