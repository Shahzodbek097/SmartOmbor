from decimal import Decimal
from django.db import transaction
from django.core.exceptions import ValidationError

from .models import Order
from inventory.models import OmborMovement


@transaction.atomic
def complete_order(order_id, user=None):

    order = Order.objects.select_for_update().get(pk=order_id)

    # Kompaniya biriktirilganligini tekshirish
    if not order.company_id:
        raise ValidationError(
            "Buyurtmaga kompaniya biriktirilmagan!"
        )

    # Foydalanuvchining kompaniyasini tekshirish
    rahbar = (
        user and user.groups.filter(name="Rahbar").exists()
    )

    if user and not user.is_superuser:
        membership = order.company.members.filter(
            user=user,
            faol=True,
            company__faol=True,
        ).exists()

        if not membership:
            raise ValidationError(
                "Siz bu kompaniyaning a'zosi emassiz!"
            )

        if not rahbar and order.customer_id != user.id:
            raise ValidationError(
                "Siz bu buyurtmani boshqarish huquqiga ega emassiz!"
            )

    # Buyurtma holatini tekshirish
    if order.status == Order.Status.COMPLETED:
        raise ValidationError("Bu buyurtma avval yakunlangan!")

    if order.status == Order.Status.CANCELLED:
        raise ValidationError(
            "Bekor qilingan buyurtmani yakunlab bo'lmaydi!"
        )

    items = order.items.select_related(
        "product"
    ).order_by("id")

    if not items.exists():
        raise ValidationError("Buyurtmada mahsulot mavjud emas!")

    total = Decimal("0.00")

    for item in items:

        if item.soni <= 0:
            raise ValidationError(
                "Mahsulot miqdori 0 dan katta bo'lishi kerak!"
            )

        if item.narxi <= 0:
            raise ValidationError("Mahsulot narxi noto'g'ri!")

        if item.product.company_id != order.company_id:
            raise ValidationError(
                "Buyurtmadagi mahsulot boshqa kompaniyaga tegishli!"
            )

        total += item.subtotal

        movement = OmborMovement(
            company=order.company,
            product=item.product,
            user=user,
            movement_type=OmborMovement.MovementType.OUT,
            nechta=item.soni,
            sababi=f"Buyurtma #{order.id}"
        )

        movement.save()

    order.total_price = total
    order.status = Order.Status.COMPLETED
    order.save(update_fields=["total_price", "status"])

    return order


@transaction.atomic
def cancel_order(order_id, user=None):

    order = Order.objects.select_for_update().get(pk=order_id)

    # Kompaniya biriktirilganligini tekshirish
    if not order.company_id:
        raise ValidationError(
            "Buyurtmaga kompaniya biriktirilmagan!"
        )

    # Foydalanuvchining kompaniyasini tekshirish
    rahbar = (
        user and user.groups.filter(name="Rahbar").exists()
    )

    if user and not user.is_superuser:
        membership = order.company.members.filter(
            user=user,
            faol=True,
            company__faol=True,
        ).exists()

        if not membership:
            raise ValidationError(
                "Siz bu kompaniyaning a'zosi emassiz!"
            )

        if not rahbar and order.customer_id != user.id:
            raise ValidationError(
                "Siz bu buyurtmani boshqarish huquqiga ega emassiz!"
            )

    if order.status == Order.Status.CANCELLED:
        raise ValidationError(
            "Bu buyurtma avval bekor qilingan!"
        )

    if order.status == Order.Status.COMPLETED:
        raise ValidationError(
            "Yakunlangan buyurtmani bekor qilib bo'lmaydi!"
        )

    order.status = Order.Status.CANCELLED
    order.save(update_fields=["status"])

    return order