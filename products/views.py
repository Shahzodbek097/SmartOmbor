
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.db import IntegrityError

from .models import Product, Category
from .forms import ProductForm, CategoryForm
from accounts.decorators import permission_required


@permission_required("products.view_product")
def product_list(request):
    mahsulotlar = Product.objects.select_related(
        "category"
    ).order_by("-created_at")

    # Qidiruv
    qidiruv = request.GET.get("q", "").strip()

    if qidiruv:
        mahsulotlar = mahsulotlar.filter(
            Q(nomi__icontains=qidiruv)
        )

    # Kategoriya bo'yicha filter
    kategoriya_id = request.GET.get("category", "")

    if kategoriya_id:
        mahsulotlar = mahsulotlar.filter(
            category_id=kategoriya_id
        )

    # Sahifalash
    paginator = Paginator(mahsulotlar, 5)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(request, "products/product_list.html", {
        "mahsulotlar": page_obj,
        "page_obj": page_obj,
        "qidiruv": qidiruv,
        "kategoriya_id": kategoriya_id,
        "kategoriyalar": Category.objects.all(),
    })


@permission_required("products.add_product")
def product_create(request):
    form = ProductForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(
            request,
            "Mahsulot muvaffaqiyatli qo‘shildi!"
        )
        return redirect("products:product_list")

    return render(request, "products/product_form.html", {
        "form": form,
        "sarlavha": "Yangi mahsulot qo‘shish"
    })


@permission_required("products.change_product")
def product_update(request, product_id):
    mahsulot = get_object_or_404(
        Product,
        id=product_id
    )

    form = ProductForm(
        request.POST or None,
        instance=mahsulot
    )

    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(
            request,
            "Mahsulot yangilandi!"
        )
        return redirect("products:product_list")

    return render(request, "products/product_form.html", {
        "form": form,
        "sarlavha": "Mahsulotni tahrirlash"
    })


@permission_required("products.view_category")
def category_list(request):
    kategoriyalar = Category.objects.order_by("nomi")

    return render(request, "products/category_list.html", {
        "kategoriyalar": kategoriyalar
    })


@permission_required("products.add_category")
def category_create(request):
    form = CategoryForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        try:
            form.save()
            messages.success(
                request,
                "Kategoriya muvaffaqiyatli qo‘shildi!"
            )
            return redirect("products:category_list")

        except IntegrityError:
            messages.error(
                request,
                "Bu kategoriya allaqachon mavjud."
            )

    return render(request, "products/category_form.html", {
        "form": form,
        "sarlavha": "Yangi kategoriya qo‘shish"
    })


@permission_required("products.change_category")
def category_update(request, category_id):
    kategoriya = get_object_or_404(
        Category,
        id=category_id
    )

    form = CategoryForm(
        request.POST or None,
        instance=kategoriya
    )

    if request.method == "POST" and form.is_valid():
        try:
            form.save()
            messages.success(
                request,
                "Kategoriya yangilandi!"
            )
            return redirect("products:category_list")

        except IntegrityError:
            messages.error(
                request,
                "Bu nomdagi kategoriya allaqachon mavjud."
            )

    return render(request, "products/category_form.html", {
        "form": form,
        "sarlavha": "Kategoriyani tahrirlash"
    })
