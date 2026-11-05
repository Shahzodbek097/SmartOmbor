from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.paginator import Paginator
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import transaction

from accounts.decorators import role_required
from .models import OmborMovement
from .forms import OmborMovementForm

User = get_user_model()


@role_required("Omborchi")
def movement_list(request):
    movements = OmborMovement.objects.select_related(
        "product",
        "user"
    ).order_by("-created_at")

    # Mahsulot nomi bo'yicha qidirish
    qidiruv = request.GET.get("q", "").strip()

    if qidiruv:
        movements = movements.filter(
            product__nomi__icontains=qidiruv
        )

    # Harakat turi bo'yicha filter
    harakat_turi = request.GET.get("movement_type", "")

    if harakat_turi in ["IN", "OUT"]:
        movements = movements.filter(
            movement_type=harakat_turi
        )

    # Boshlanish sanasi
    sana_boshi = request.GET.get("date_from", "")

    if sana_boshi:
        movements = movements.filter(
            created_at__date__gte=sana_boshi
        )

    # Tugash sanasi
    sana_oxiri = request.GET.get("date_to", "")

    if sana_oxiri:
        movements = movements.filter(
            created_at__date__lte=sana_oxiri
        )

    # Xodim bo'yicha
    user_id = request.GET.get("user", "")

    if user_id:
        movements = movements.filter(user_id=user_id)

    # Pagination
    paginator = Paginator(movements, 10)
    page_obj = paginator.get_page(request.GET.get("page"))

    return render(request, "inventory/movement_list.html", {
        "movements": page_obj,
        "page_obj": page_obj,
        "qidiruv": qidiruv,
        "harakat_turi": harakat_turi,
        "sana_boshi": sana_boshi,
        "sana_oxiri": sana_oxiri,
        "users": User.objects.filter(
            ombor_harakatlari__isnull=False
        ).distinct(),
        "user_id": user_id,
    })


@role_required("Omborchi")
def movement_create(request):
    if request.method == "POST":
        form = OmborMovementForm(request.POST)

        if form.is_valid():
            try:
                with transaction.atomic():
                    movement = form.save(commit=False)
                    movement.user = request.user
                    movement.save()

                messages.success(
                    request,
                    "Ombor harakati muvaffaqiyatli saqlandi."
                )

                return redirect("inventory:movement_list")

            except ValidationError as error:
                messages.error(
                    request,
                    "; ".join(error.messages)
                )

    else:
        form = OmborMovementForm()

    context = {
        "form": form,
    }

    return render(
        request,
        "inventory/movement_form.html",
        context,
    )

