from celery import shared_task
from django.core.mail import send_mail
from django.utils import timezone

from companies.models import Company, CompanyMembership
from reports.services import (
    get_low_stock_products,
    get_period_report,
)


@shared_task
def generate_low_stock_report(company_id):
    """
    Kompaniyaning kam qolgan mahsulotlarini
    fon rejimida aniqlaydi.
    """

    try:
        company = Company.objects.get(
            id=company_id,
            faol=True
        )
    except Company.DoesNotExist:
        return {
            "success": False,
            "message": "Kompaniya topilmadi yoki faol emas."
        }

    products = get_low_stock_products(company)

    product_list = [
        {
            "id": product.id,
            "nomi": product.nomi,
            "qoldiq": product.qoldiq,
            "min_qoldiq": product.min_qoldiq,
        }
        for product in products
    ]

    return {
        "success": True,
        "company": company.nomi,
        "count": len(product_list),
        "products": product_list,
    }


@shared_task
def send_low_stock_alert(company_id):
    """
    Kam qolgan mahsulotlar haqida
    kompaniya Rahbarlariga email yuboradi.
    """

    try:
        company = Company.objects.get(
            id=company_id,
            faol=True
        )
    except Company.DoesNotExist:
        return {
            "success": False,
            "message": "Kompaniya topilmadi."
        }

    products = get_low_stock_products(company)

    if not products.exists():
        return {
            "success": True,
            "message": "Kam qolgan mahsulotlar mavjud emas."
        }

    emails = list(
        CompanyMembership.objects.filter(
            company=company,
            role="Rahbar",
            faol=True,
            company__faol=True,
            user__is_active=True,
        ).exclude(
            user__email=""
        ).values_list(
            "user__email",
            flat=True
        ).distinct()
    )

    if not emails:
        return {
            "success": False,
            "message": "Rahbarlarning email manzili topilmadi."
        }

    satrlar = [
        f"- {product.nomi}: {product.qoldiq} dona "
        f"(minimal: {product.min_qoldiq} dona)"
        for product in products
    ]

    message = (
        f"Hurmatli {company.nomi} rahbari!\n\n"
        "Quyidagi mahsulotlarning ombordagi qoldig'i kamaygan:\n\n"
        + "\n".join(satrlar)
        + "\n\nSmartOmbor avtomatik xabarnomasi."
    )

    yuborildi = send_mail(
        subject=f"{company.nomi} — Omborda kam qolgan mahsulotlar",
        message=message,
        from_email=None,
        recipient_list=emails,
        fail_silently=False,
    )

    return {
        "success": bool(yuborildi),
        "recipients": len(emails),
        "products_count": products.count(),
    }



@shared_task
def generate_daily_sales_report(company_id):
    """
    Kompaniyaning kunlik savdo hisobotini
    hisoblaydi va Rahbarlarga email yuboradi.
    """

    try:
        company = Company.objects.get(
            id=company_id,
            faol=True
        )
    except Company.DoesNotExist:
        return {
            "success": False,
            "message": "Kompaniya topilmadi."
        }

    today = timezone.localdate()

    report = get_period_report(
        company,
        today,
        today
    )

    # Faol Rahbarlarning email manzillarini olish
    emails = list(
        CompanyMembership.objects.filter(
            company=company,
            role="Rahbar",
            faol=True,
            company__faol=True,
            user__is_active=True,
        ).exclude(
            user__email=""
        ).values_list(
            "user__email",
            flat=True
        ).distinct()
    )

    if not emails:
        return {
            "success": False,
            "message": "Rahbarlarning email manzili topilmadi."
        }

    buyurtmalar = report["buyurtmalar_soni"]
    savdo = report["savdo_summasi"]
    mahsulotlar = report["sotilgan_mahsulotlar"]
    foyda = report["foyda"]

    message = (
        f"Hurmatli {company.nomi} rahbari!\n\n"
        f"{today.strftime('%d.%m.%Y')} kunlik savdo hisoboti.\n\n"
        f"KOMPANIYA: {company.nomi}\n\n"
        f"Buyurtmalar soni: {buyurtmalar}\n"
        f"Jami savdo: {savdo} so'm\n"
        f"Sotilgan mahsulotlar: {mahsulotlar} dona\n"
        f"Yalpi foyda: {foyda} so'm\n\n"
        "Hisobot SmartOmbor tizimi tomonidan "
        "avtomatik shakllantirildi."
    )

    yuborildi = send_mail(
        subject=f"{company.nomi} — Kunlik savdo hisoboti",
        message=message,
        from_email=None,
        recipient_list=emails,
        fail_silently=False,
    )

    return {
        "success": yuborildi == 1,
        "company": company.nomi,
        "sana": today.isoformat(),
        "recipients": len(emails),
        "buyurtmalar_soni": buyurtmalar,
        "savdo_summasi": str(savdo),
        "foyda": str(foyda),
    }



@shared_task
def generate_all_daily_sales_reports():
    """
    Barcha faol kompaniyalar uchun
    kunlik savdo hisobotlarini navbatga yuboradi.
    """

    companies = Company.objects.filter(
        faol=True
    ).values_list("id", flat=True)

    task_ids = []

    for company_id in companies:
        result = generate_daily_sales_report.delay(
            company_id
        )

        task_ids.append({
            "company_id": company_id,
            "task_id": result.id
        })

    return {
        "success": True,
        "companies_count": len(task_ids),
        "tasks": task_ids
    }


@shared_task
def send_all_low_stock_alerts():
    """
    Barcha faol kompaniyalarning Rahbarlariga
    kam qolgan mahsulotlar haqida xabar yuboradi.
    """

    company_ids = Company.objects.filter(
        faol=True
    ).values_list("id", flat=True)

    task_ids = []

    for company_id in company_ids:
        result = send_low_stock_alert.delay(company_id)

        task_ids.append({
            "company_id": company_id,
            "task_id": result.id
        })

    return {
        "success": True,
        "companies_count": len(task_ids),
        "tasks": task_ids
    }
