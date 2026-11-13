from django.urls import path
from .views import *

app_name = "sales"


urlpatterns = [
    path("",order_list,name="order_list"),
    path("create/",order_create,name="order_create"),
    path("<int:order_id>/",order_detail,name="order_detail"),
    path("<int:order_id>/finish/",order_finish,name="order_finish"),
    path("<int:order_id>/cancel/",order_cancel,name="order_cancel"),
    path("<int:order_id>/delete/",order_delete,name="order_delete"),
    path("manager/", manager_order_list, name="manager_order_list"),
]
