from django.urls import path
from views import *

app_name = "products"

urlpatterns = [
    path("", product_list, name="product_list"),
    path("create/", product_create, name="product_create"),
    path("<int:product_id>/edit/", product_update, name="product_update"),

    path("categories/", category_list, name="category_list"),
    path("categories/create/", category_create, name="category_create"),
    path("categories/<int:category_id>/edit/",category_update,name="category_update"),
]