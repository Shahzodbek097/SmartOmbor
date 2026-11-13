from django.urls import path
from .views import *

app_name = "inventory"

urlpatterns = [
    path("",movement_list,name="movement_list"),
    path("create/",movement_create,name="movement_create"),
]
