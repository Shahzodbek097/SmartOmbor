from django.shortcuts import render
from accounts.decorators import role_required
from django.utils.dateparse import parse_date
from django.http import HttpResponse
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.utils import get_column_letter
from io import BytesIO
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.platypus import (
    SimpleDocTemplate,
    Table,
    TableStyle,
    Paragraph,
    Spacer
)
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import mm
from companies.utils import get_user_company

from .services import (
    get_daily_report,
    get_monthly_report,
    get_low_stock_products,
    get_sellers_report,
    get_period_report,
    get_period_sales_chart,
    get_period_top_products,
    get_inventory_report,
    get_inventory_chart,
    get_product_inventory_chart
)

@role_required("Rahbar", "Omborchi", "Sotuvchi")
def dashboard(request):
    company = get_user_company(request.user)

    sana_boshi = request.GET.get("date_from", "")
    sana_oxiri = request.GET.get("date_to", "")

    boshlanish = parse_date(sana_boshi) if sana_boshi else None
    tugash = parse_date(sana_oxiri) if sana_oxiri else None

    davr = get_period_report(company, boshlanish, tugash)

    membership = request.user.company_memberships.filter(
        company=company,
        faol=True,
        company__faol=True
    ).first()

    is_rahbar = (
            request.user.is_superuser
            or bool(membership and membership.role == "Rahbar")
    )

    is_omborchi = bool(
        membership and membership.role == "Omborchi"
    )

    is_sotuvchi = bool(
        membership and membership.role == "Sotuvchi"
    )

    context = {
        "davr": davr,
        "davr_grafigi": get_period_sales_chart(
            company, boshlanish, tugash
        ),
        "davr_top_mahsulotlar": get_period_top_products(
            company, boshlanish, tugash
        ),
        "kam_qolgan": get_low_stock_products(company),
        "sana_boshi": sana_boshi,
        "sana_oxiri": sana_oxiri,
        "is_rahbar": is_rahbar,
        "is_omborchi": is_omborchi,
        "is_sotuvchi": is_sotuvchi,
    }

    return render(request, "reports/dashboard.html", context)


@role_required("Rahbar")
def sellers_report(request):
    company = get_user_company(request.user)

    sana_boshi = request.GET.get("date_from", "")
    sana_oxiri = request.GET.get("date_to", "")

    boshlanish = parse_date(sana_boshi) if sana_boshi else None
    tugash = parse_date(sana_oxiri) if sana_oxiri else None

    context = {
        "sotuvchilar": get_sellers_report(
            company,
            boshlanish,
            tugash
        ),
        "sana_boshi": sana_boshi,
        "sana_oxiri": sana_oxiri,
    }

    return render(
        request,
        "reports/sellers_report.html",
        context
    )

def excel_response(workbook, filename):
    response = HttpResponse(
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

    response["Content-Disposition"] = (
        f'attachment; filename="{filename}"'
    )

    workbook.save(response)

    return response


def excel_header(sheet):
    for cell in sheet[1]:
        cell.font = Font(bold=True, color="FFFFFF")
        cell.fill = PatternFill(
            start_color="1F4E78",
            end_color="1F4E78",
            fill_type="solid"
        )
        cell.alignment = Alignment(horizontal="center")

    for column in sheet.columns:
        max_length = max(
            len(str(cell.value or ""))
            for cell in column
        )
        sheet.column_dimensions[
            get_column_letter(column[0].column)
        ].width = min(max_length + 4, 35)


@role_required("Rahbar")
def export_dashboard_excel(request):
    company = get_user_company(request.user)

    sana_boshi = request.GET.get("date_from", "")
    sana_oxiri = request.GET.get("date_to", "")

    boshlanish = parse_date(sana_boshi) if sana_boshi else None
    tugash = parse_date(sana_oxiri) if sana_oxiri else None

    report = get_period_report(
        company,
        boshlanish,
        tugash
    )

    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "Dashboard hisoboti"

    sheet.append(["Kompaniya", company.nomi])
    sheet.append(["Ko‘rsatkich", "Natija"])

    sheet.append(["Buyurtmalar soni", report["buyurtmalar_soni"]])
    sheet.append(["Savdo summasi", float(report["savdo_summasi"])])
    sheet.append(["Sotilgan mahsulotlar", report["sotilgan_mahsulotlar"]])
    sheet.append(["Foyda", float(report["foyda"])])

    sheet.append(["Boshlanish sanasi", sana_boshi or "Barcha vaqt"])
    sheet.append(["Tugash sanasi", sana_oxiri or "Barcha vaqt"])

    excel_header(sheet)

    return excel_response(workbook, "dashboard_hisoboti.xlsx")


@role_required("Rahbar")
def export_sellers_excel(request):
    company = get_user_company(request.user)

    sana_boshi = request.GET.get("date_from", "")
    sana_oxiri = request.GET.get("date_to", "")

    boshlanish = parse_date(sana_boshi) if sana_boshi else None
    tugash = parse_date(sana_oxiri) if sana_oxiri else None

    sellers = get_sellers_report(
        company,
        boshlanish,
        tugash
    )

    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "Sotuvchilar hisoboti"

    sheet.append(["Kompaniya", company.nomi])
    sheet.append([])
    sheet.append([
        "Sotuvchi",
        "Jami buyurtmalar",
        "Yakunlangan",
        "Bekor qilingan",
        "Sotilgan mahsulotlar",
        "Savdo summasi"
    ])

    for seller in sellers:
        sheet.append([
            seller["customer__username"],
            seller["jami_buyurtmalar"],
            seller["yakunlangan_buyurtmalar"],
            seller["bekor_qilingan_buyurtmalar"],
            seller["sotilgan_mahsulotlar"],
            float(seller["savdo_summasi"])
        ])

    excel_header(sheet)

    return excel_response(workbook, "sotuvchilar_hisoboti.xlsx")


def create_pdf(title, headers, data, filename):
    buffer = BytesIO()

    document = SimpleDocTemplate(
        buffer,
        pagesize=landscape(A4),
        rightMargin=15 * mm,
        leftMargin=15 * mm,
        topMargin=15 * mm,
        bottomMargin=15 * mm
    )

    styles = getSampleStyleSheet()

    elements = []

    elements.append(Paragraph(title, styles["Title"]))
    elements.append(Spacer(1, 15))

    table_data = [headers] + data

    table = Table(table_data, repeatRows=1)

    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1F4E78")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("PADDING", (0, 0), (-1, -1), 8),
    ]))

    elements.append(table)

    document.build(elements)

    buffer.seek(0)

    response = HttpResponse(
        buffer.getvalue(),
        content_type="application/pdf"
    )

    response["Content-Disposition"] = (
        f'attachment; filename="{filename}"'
    )

    return response


@role_required("Rahbar")
def export_dashboard_pdf(request):
    company = get_user_company(request.user)
    sana_boshi = request.GET.get("date_from", "")
    sana_oxiri = request.GET.get("date_to", "")

    boshlanish = parse_date(sana_boshi) if sana_boshi else None
    tugash = parse_date(sana_oxiri) if sana_oxiri else None

    report = get_period_report(company, boshlanish, tugash)

    data = [
        ["Kompaniya", company.nomi],
        ["Buyurtmalar soni", report["buyurtmalar_soni"]],
        ["Savdo summasi", f'{report["savdo_summasi"]} so‘m'],
        ["Sotilgan mahsulotlar", report["sotilgan_mahsulotlar"]],
        ["Foyda", f'{report["foyda"]} so‘m'],
        ["Boshlanish sanasi", sana_boshi or "Barcha vaqt"],
        ["Tugash sanasi", sana_oxiri or "Barcha vaqt"],
    ]

    return create_pdf(
        "SmartOmbor — Bosh menu hisoboti",
        ["Ko‘rsatkich", "Natija"],
        data,
        "bosh_menu_hisoboti.pdf"
    )


@role_required("Rahbar")
def export_sellers_pdf(request):
    company = get_user_company(request.user)
    sana_boshi = request.GET.get("date_from", "")
    sana_oxiri = request.GET.get("date_to", "")

    boshlanish = parse_date(sana_boshi) if sana_boshi else None
    tugash = parse_date(sana_oxiri) if sana_oxiri else None

    sellers = get_sellers_report(company, boshlanish, tugash)

    data = []

    data.append(["Kompaniya", company.nomi])
    data.append([])

    for seller in sellers:
        data.append([
            seller["customer__username"],
            seller["jami_buyurtmalar"],
            seller["yakunlangan_buyurtmalar"],
            seller["bekor_qilingan_buyurtmalar"],
            seller["sotilgan_mahsulotlar"],
            f'{seller["savdo_summasi"]} so‘m',
        ])

    return create_pdf(
        "SmartOmbor — Sotuvchilar hisoboti",
        [
            "Sotuvchi",
            "Jami buyurtma",
            "Yakunlangan",
            "Bekor qilingan",
            "Sotilgan mahsulot",
            "Savdo summasi",
        ],
        data,
        "sotuvchilar_hisoboti.pdf"
    )

@role_required("Rahbar")
def inventory_report(request):
    company = get_user_company(request.user)
    sana_boshi = request.GET.get("date_from", "")
    sana_oxiri = request.GET.get("date_to", "")

    boshlanish = parse_date(sana_boshi) if sana_boshi else None
    tugash = parse_date(sana_oxiri) if sana_oxiri else None

    report = get_inventory_report(company, boshlanish, tugash)

    context = {
        "report": report,
        "sana_boshi": sana_boshi,
        "sana_oxiri": sana_oxiri,
        "inventory_chart": get_inventory_chart(company, boshlanish, tugash),
        "product_inventory_chart": get_product_inventory_chart(
            company, boshlanish, tugash
        ),
    }

    return render(
        request,
        "reports/inventory_report.html",
        context
    )

@role_required("Rahbar")
def export_inventory_excel(request):
    company = get_user_company(request.user)
    sana_boshi = request.GET.get("date_from", "")
    sana_oxiri = request.GET.get("date_to", "")

    boshlanish = parse_date(sana_boshi) if sana_boshi else None
    tugash = parse_date(sana_oxiri) if sana_oxiri else None

    report = get_inventory_report(company, boshlanish, tugash)

    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "Ombor hisoboti"

    # Sarlavha
    sheet.merge_cells("A1:E1")
    sheet["A1"] = "SMARTOMBOR — OMBOR HISOBOTI"
    sheet["A1"].font = Font(bold=True, size=16)
    sheet["A1"].alignment = Alignment(horizontal="center")

    # Sana oralig'i
    sheet["A3"] = "Boshlanish sanasi:"
    sheet["B3"] = sana_boshi or "Barcha vaqt"

    sheet["A4"] = "Tugash sanasi:"
    sheet["B4"] = sana_oxiri or "Barcha vaqt"

    # Umumiy ko'rsatkichlar
    sheet["A6"] = "Jami kirim"
    sheet["B6"] = report["jami_kirim"]

    sheet["A7"] = "Jami chiqim"
    sheet["B7"] = report["jami_chiqim"]

    sheet["A8"] = "Kirim harakatlari"
    sheet["B8"] = report["kirim_harakatlari"]

    sheet["A9"] = "Chiqim harakatlari"
    sheet["B9"] = report["chiqim_harakatlari"]

    sheet.append(["Kompaniya", company.nomi])
    sheet.append([])

    # Mahsulotlar jadvali
    headers = [
        "№",
        "Mahsulot nomi",
        "Kirim",
        "Chiqim",
        "Joriy qoldiq",
    ]

    header_row = 11

    for col, header in enumerate(headers, start=1):
        cell = sheet.cell(row=header_row, column=col)
        cell.value = header
        cell.font = Font(bold=True, color="FFFFFF")
        cell.fill = PatternFill(
            start_color="343A40",
            end_color="343A40",
            fill_type="solid"
        )
        cell.alignment = Alignment(horizontal="center")

    for index, mahsulot in enumerate(report["mahsulotlar"], start=1):
        row = header_row + index

        sheet.cell(row=row, column=1, value=index)
        sheet.cell(row=row, column=2, value=mahsulot.nomi)
        sheet.cell(row=row, column=3, value=mahsulot.jami_kirim or 0)
        sheet.cell(row=row, column=4, value=mahsulot.jami_chiqim or 0)
        sheet.cell(row=row, column=5, value=mahsulot.qoldiq)

    # Ustun kengliklari
    widths = {
        "A": 8,
        "B": 30,
        "C": 18,
        "D": 18,
        "E": 20,
    }

    for column, width in widths.items():
        sheet.column_dimensions[column].width = width

    # HTTP javob
    response = HttpResponse(
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

    response["Content-Disposition"] = (
        'attachment; filename="ombor_hisoboti.xlsx"'
    )

    workbook.save(response)

    return response

@role_required("Rahbar")
def export_inventory_pdf(request):
    company = get_user_company(request.user)
    sana_boshi = request.GET.get("date_from", "")
    sana_oxiri = request.GET.get("date_to", "")

    boshlanish = parse_date(sana_boshi) if sana_boshi else None
    tugash = parse_date(sana_oxiri) if sana_oxiri else None

    report = get_inventory_report(company, boshlanish, tugash)

    buffer = BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=landscape(A4),
        rightMargin=25,
        leftMargin=25,
        topMargin=30,
        bottomMargin=30,
    )

    styles = getSampleStyleSheet()
    elements = []

    elements.append(
        Paragraph("SMARTOMBOR - OMBOR HISOBOTI", styles["Title"])
    )
    elements.append(Spacer(1, 15))

    elements.append(
        Paragraph(
            f"Sana: {sana_boshi or 'Barcha vaqt'} - "
            f"{sana_oxiri or 'Barcha vaqt'}",
            styles["Normal"],
        )
    )
    elements.append(Spacer(1, 15))

    elements.append(
        Paragraph(
            f"Jami kirim: {report['jami_kirim']} dona",
            styles["Normal"],
        )
    )
    elements.append(
        Paragraph(
            f"Jami chiqim: {report['jami_chiqim']} dona",
            styles["Normal"],
        )
    )
    elements.append(
        Paragraph(
            f"Kirim harakatlari: {report['kirim_harakatlari']}",
            styles["Normal"],
        )
    )
    elements.append(
        Paragraph(
            f"Chiqim harakatlari: {report['chiqim_harakatlari']}",
            styles["Normal"],
        )
    )

    elements.append(Spacer(1, 20))

    data = [
        ["Kompaniya", company.nomi],
        [],
        ["№", "Mahsulot nomi", "Kirim", "Chiqim", "Joriy qoldiq"]
    ]

    for index, mahsulot in enumerate(report["mahsulotlar"], start=1):
        data.append([
            index,
            mahsulot.nomi,
            mahsulot.jami_kirim or 0,
            mahsulot.jami_chiqim or 0,
            mahsulot.qoldiq,
        ])

    table = Table(
        data,
        colWidths=[40, 250, 100, 100, 120],
        repeatRows=1,
    )

    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#343A40")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("PADDING", (0, 0), (-1, -1), 7),
    ]))

    elements.append(table)

    doc.build(elements)

    pdf = buffer.getvalue()
    buffer.close()

    response = HttpResponse(
        content_type="application/pdf"
    )
    response["Content-Disposition"] = (
        'attachment; filename="ombor_hisoboti.pdf"'
    )
    response.write(pdf)

    return response