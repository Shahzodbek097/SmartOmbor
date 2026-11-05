from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from django.shortcuts import render


urlpatterns = [
    path(
        "reset/<uidb64>/<token>/",
        auth_views.PasswordResetConfirmView.as_view(
            template_name="registration/password_reset_confirm.html",
            success_url="/accounts/reset/done/",
        ),
        name="password_reset_confirm",
    ),
    path('admin/', admin.site.urls),
    path('dashboard/', include('reports.urls')),
    path('accounts/', include('accounts.urls')),
    path('inventory/', include('inventory.urls')),
    path('sales/', include('sales.urls')),
    path('products/', include('products.urls')),
    path('accounts/', include('accounts.urls')),
]

def custom_403(request, exception):
    return render(request, "403.html", status=403)


handler403 = custom_403