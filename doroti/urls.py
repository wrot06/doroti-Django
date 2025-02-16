from django.contrib import admin
from django.urls import path, include  # Agrega include aquí

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("aplicacion1.urls")),  # Asegúrate de que el nombre de la app es correcto
]
