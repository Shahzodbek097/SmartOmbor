from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from django.shortcuts import render


from rest_framework import permissions
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from api.views import CompanyTokenObtainPairView, CompanyTokenRefreshView


schema_view = get_schema_view(
    openapi.Info(
        title="SmartOmbor API",
        default_version="v1",
        description=(
            "SmartOmbor — ombor, mahsulot, "
            "savdo va buyurtmalarni boshqarish API."
        ),
        contact=openapi.Contact(
            email="support@smartombor.uz"
        ),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)


urlpatterns = [
    path("api/auth/",include("djoser.urls")),
    path("api/v1/", include("api.urls")),
    path("api/token/",CompanyTokenObtainPairView.as_view(),name="token_obtain_pair"),
    path("api/token/refresh/",CompanyTokenRefreshView.as_view(),name="token_refresh"),
    path("swagger/",schema_view.with_ui("swagger", cache_timeout=0),name="schema-swagger-ui"),
    path("redoc/",schema_view.with_ui("redoc", cache_timeout=0),name="schema-redoc"),
    path("reset/<uidb64>/<token>/",auth_views.PasswordResetConfirmView.as_view(template_name="registration/password_reset_confirm.html",success_url="/accounts/reset/done/",),
         name="password_reset_confirm",
    ),


    path('admin/', admin.site.urls),
    path('dashboard/', include('reports.urls')),
    path('accounts/', include('accounts.urls')),
    path('inventory/', include('inventory.urls')),
    path('sales/', include('sales.urls')),
    path('products/', include('products.urls')),
]

def custom_403(request, exception):
    return render(request, "403.html", status=403)


handler403 = custom_403