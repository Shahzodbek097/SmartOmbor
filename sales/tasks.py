from celery import shared_task
from django.utils import timezone
from django.core.mail import send_mail
from sales.models import Order


@shared_task
def send_order_completed_email(order_id):
    """
    Buyurtma yakunlanganda mijozga email yuboradi.
    """

    try:
        order = Order.objects.select_related(
            "company",
            "customer"
        ).prefetch_related(
            "items__product"
        ).get(pk=order_id)

    except Order.DoesNotExist:
        return {
            "success": False,
            "message": "Buyurtma topilmadi."
        }

    # Faqat yakunlangan buyurtmaga email yuboriladi.
    if order.status != Order.Status.COMPLETED:
        return {
            "success": False,
            "message": "Buyurtma hali yakunlanmagan."
        }

    # Mijoz emailini tekshirish
    email = (order.customer.email or "").strip()

    if not email:
        return {
            "success": False,
            "message": "Mijozning email manzili mavjud emas."
        }

    # Buyurtmadagi mahsulotlarni tayyorlash
    mahsulotlar = []

    for item in order.items.all():

        mahsulotlar.append(
            f"{item.product.nomi}\n"
            f"Miqdor: {item.soni} dona\n"
            f"Narxi: {item.narxi:.2f} so'm\n"
            f"Jami: {item.subtotal:.2f} so'm"
        )

    ism = (
        order.customer.get_full_name()
        or order.customer.username
    )

    buyurtma_vaqti = timezone.localtime(order.created_at)

    message = (
        f"Assalomu alaykum, {ism}!\n\n"
        f"Sizning buyurtmangiz muvaffaqiyatli yakunlandi.\n\n"
        f"Kompaniya: {order.company.nomi}\n"
        f"Buyurtma raqami: #{order.buyurtma_raqami}\n"
        f"Buyurtma vaqti: {buyurtma_vaqti.strftime('%d.%m.%Y %H:%M')} (Toshkent vaqti)\n\n"
        f"BUYURTMA TARKIBI:\n\n"
        + "\n\n".join(mahsulotlar)
        + "\n\n"
        f"Umumiy summa: {order.total_price:.2f} so'm\n\n"
        "Xaridingiz uchun rahmat!\n"
        "SmartOmbor jamoasi."
    )

    yuborildi = send_mail(
        subject=(
            f"SmartOmbor — "
            f"Buyurtma #{order.buyurtma_raqami} yakunlandi"
        ),
        message=message,
        from_email=None,
        recipient_list=[email],
        fail_silently=False,
    )

    return {
        "success": yuborildi == 1,
        "recipient": email,
        "order_id": order.id,
    }
