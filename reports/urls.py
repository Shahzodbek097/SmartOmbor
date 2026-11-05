from django.urls import path
from .views import *

app_name = "reports"

urlpatterns = [
    path("", dashboard, name="dashboard"),
    path("sellers/", sellers_report, name="sellers_report"),
    path("export/menu/", export_dashboard_excel, name="export_dashboard_excel"),
    path("export/sellers/", export_sellers_excel, name="export_sellers_excel"),
    path("export/menu/pdf/",export_dashboard_pdf, name="export_dashboard_pdf"),
    path("export/sellers/pdf/",export_sellers_pdf, name="export_sellers_pdf"),
    path("inventory/",inventory_report,name="inventory_report"),
    path("export/inventory/",export_inventory_excel,name="export_inventory_excel"),
    path("export/inventory/pdf/",export_inventory_pdf,name="export_inventory_pdf"),
]