from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.exceptions import ValidationError, PermissionDenied
from django.db import transaction
from django.core.paginator import Paginator

from accounts.decorators import role_required, permission_required
from .models import Order, OrderItem
from .forms import OrderItemFormSet
from .services import complete_order, cancel_order


@role_required("Sotuvchi")
def order_list(request):
    orders = Order.objects.filter(
        customer=request.user
    ).order_by("-created_at")

    # Buyurtma raqami bo'yicha qidirish
    qidiruv = request.GET.get("q", "").strip()

    if qidiruv.isdigit():
        orders = orders.filter(id=int(qidiruv))

    # Buyurtma holati
    holat = request.GET.get("status", "")

    if holat in ["PENDING", "COMPLETED", "CANCELLED"]:
        orders = orders.filter(status=holat)

    # Sana bo'yicha filter
    sana_boshi = request.GET.get("date_from", "")
    sana_oxiri = request.GET.get("date_to", "")

    if sana_boshi:
        orders = orders.filter(created_at__date__gte=sana_boshi)

    if sana_oxiri:
        orders = orders.filter(created_at__date__lte=sana_oxiri)

    # Pagination
    paginator = Paginator(orders, 10)
    page_obj = paginator.get_page(request.GET.get("page"))

    return render(request, "sales/order_list.html", {
        "orders": page_obj,
        "page_obj": page_obj,
        "qidiruv": qidiruv,
        "holat": holat,
        "sana_boshi": sana_boshi,
        "sana_oxiri": sana_oxiri,
    })


@role_required("Sotuvchi")
def order_create(request):
    if request.method == "POST":
        formset = OrderItemFormSet(request.POST)

        if formset.is_valid():
            with transaction.atomic():
                buyurtma = Order.objects.create(
                    customer=request.user,
                )

                for form in formset:
                    if not form.cleaned_data:
                        continue

                    if form.cleaned_data.get("DELETE"):
                        continue

                    product = form.cleaned_data["product"]
                    soni = form.cleaned_data["soni"]

                    OrderItem.objects.create(
                        order=buyurtma,
                        product=product,
                        soni=soni,
                        narxi=product.sotish_narxi,
                    )

            messages.success(
                request,
                "Buyurtma muvaffaqiyatli yaratildi.",
            )

            return redirect(
                "sales:order_detail",
                order_id=buyurtma.id,
            )

    else:
        formset = OrderItemFormSet()

    return render(
        request,
        "sales/order_form.html",
        {"formset": formset},
    )


@role_required("Sotuvchi", "Rahbar")
def order_detail(request, order_id):
    order = get_object_or_404(
        Order.objects.prefetch_related("items__product"),
        id=order_id
    )

    # Superuser va Rahbar barcha buyurtmalarni ko‘ra oladi
    rahbar = request.user.groups.filter(name="Rahbar").exists()

    # Sotuvchi faqat o‘z buyurtmasini ko‘ra oladi
    if not request.user.is_superuser and not rahbar:
        if order.customer_id != request.user.id:
            raise PermissionDenied

    return render(
        request,
        "sales/order_detail.html",
        {"order": order}
    )


@role_required("Sotuvchi")
def order_finish(request, order_id):
    if request.method != "POST":
        return redirect("sales:order_list")

    buyurtma = get_object_or_404(
        Order,
        id=order_id,
        customer=request.user,
    )

    try:
        complete_order(buyurtma.id, user=request.user)

        messages.success(
            request,
            "Buyurtma yakunlandi.",
        )

    except ValidationError as error:
        messages.error(
            request,
            "; ".join(error.messages),
        )

    return redirect(
        "sales:order_detail",
        order_id=buyurtma.id,
    )


@role_required("Sotuvchi")
def order_cancel(request, order_id):
    if request.method != "POST":
        return redirect("sales:order_list")

    buyurtma = get_object_or_404(
        Order,
        id=order_id,
        customer=request.user,
    )

    try:
        cancel_order(buyurtma.id, user=request.user)

        messages.success(
            request,
            "Buyurtma bekor qilindi.",
        )

    except ValidationError as error:
        messages.error(
            request,
            "; ".join(error.messages),
        )

    return redirect(
        "sales:order_detail",
        order_id=buyurtma.id,
    )


@role_required("Sotuvchi", "Rahbar")
def order_delete(request, order_id):
    if request.method != "POST":
        return redirect("sales:order_list")

    buyurtma = get_object_or_404(
        Order,
        id=order_id,
    )

    # Sotuvchi faqat o'z buyurtmasini o'chira oladi
    rahbar = request.user.groups.filter(name="Rahbar").exists()

    if not request.user.is_superuser and not rahbar:
        if buyurtma.customer_id != request.user.id:
            raise PermissionDenied

    # Faqat PENDING buyurtmani o'chirish mumkin
    if buyurtma.status != "PENDING":
        messages.error(
            request,
            "Faqat kutilayotgan buyurtmalarni o'chirish mumkin.",
        )
        return redirect(
            "sales:order_detail",
            order_id=buyurtma.id,
        )

    buyurtma_id = buyurtma.id
    buyurtma.delete()

    messages.success(
        request,
        f"#{buyurtma_id}-buyurtma muvaffaqiyatli o'chirildi.",
    )

    return redirect("sales:order_list")


@permission_required("sales.view_order")
def manager_order_list(request):
    orders = Order.objects.select_related("customer").order_by("-created_at")

    # Buyurtma ID bo‘yicha qidirish
    qidiruv = request.GET.get("q", "").strip()

    if qidiruv.isdigit():
        orders = orders.filter(id=int(qidiruv))

    # Holati bo‘yicha filtrlash
    holat = request.GET.get("status", "")

    if holat in ["PENDING", "COMPLETED", "CANCELLED"]:
        orders = orders.filter(status=holat)

    # Sana bo‘yicha filtrlash
    sana_boshi = request.GET.get("date_from", "")
    sana_oxiri = request.GET.get("date_to", "")

    if sana_boshi:
        orders = orders.filter(created_at__date__gte=sana_boshi)

    if sana_oxiri:
        orders = orders.filter(created_at__date__lte=sana_oxiri)

    # Sahifalash
    paginator = Paginator(orders, 10)
    page_obj = paginator.get_page(request.GET.get("page"))

    context = {
        "orders": page_obj,
        "page_obj": page_obj,
        "qidiruv": qidiruv,
        "holat": holat,
        "sana_boshi": sana_boshi,
        "sana_oxiri": sana_oxiri,
    }

    return render(
        request,
        "sales/manager_order_list.html",
        context
    )
