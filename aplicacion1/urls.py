#aplicacion1 urls.py
from django.urls import path
from .views import (
    login_view, 
    logout_view, 
    index_view, 
    buscador_view, 
    agregar_carpeta_view, 
    indice_view, 
    tcarpeta_view, 
    agregar_capitulo_view, 
    actualizar_orden_view, 
    eliminar_capitulo_view, 
    obtener_capitulos_view,
)

urlpatterns = [
    path("", login_view, name="login"),
    path("logout/", logout_view, name="logout"),
    path("index/", index_view, name="index"),    
    path("indice/", indice_view, name="indice"),
    path("tcarpeta/", tcarpeta_view, name="tcarpeta"),
    path("buscador/", buscador_view, name="buscador"), 
    path("agregar_carpeta/", agregar_carpeta_view, name="agregar_carpeta"),
    path("agregar_capitulo/", agregar_capitulo_view, name="agregar_capitulo"),
    path("actualizar_orden/", actualizar_orden_view, name="actualizar_orden"),
    path("eliminar_capitulo/", eliminar_capitulo_view, name="eliminar_capitulo"),
    path("obtener_capitulos/", obtener_capitulos_view, name="obtener_capitulos"),
    
]
