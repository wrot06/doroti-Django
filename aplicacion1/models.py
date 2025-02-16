from django.db import models
from django.contrib.auth.models import User
from datetime import date

from django.db import models

class Subs(models.Model):
    id = models.AutoField(primary_key=True)
    serie_nombre = models.CharField(max_length=255, null=True, blank=True)  # Puede ser NULL
    nombre = models.CharField(max_length=255)  # Nombre de la subserie

    def __str__(self):
        return self.nombre


class Carpeta(models.Model):
    caja = models.PositiveIntegerField(verbose_name="Caja")
    carpeta = models.PositiveIntegerField(null=True, blank=True, verbose_name="Carpeta")
    serie = models.CharField(max_length=255, default="Serie Default")
    subs = models.CharField(max_length=255, blank=True, null=True)
    titulo = models.CharField(max_length=255, default="Título Default")
    finicial = models.DateField(default=date.today)
    ffinal = models.DateField(default=date.today)
    folios = models.PositiveIntegerField(default=1)
    fecha_ingreso = models.DateTimeField(auto_now_add=True)
    estado = models.CharField(max_length=1, default="A")
    user = models.ForeignKey(User, on_delete=models.CASCADE, default=1)  # Ajusta el default según corresponda

    def __str__(self):
        return f"Caja {self.caja} - Carpeta {self.carpeta}"





class IndiceTemp(models.Model):
    id = models.AutoField(primary_key=True)
    id2 = models.IntegerField()
    Caja = models.IntegerField(null=True, blank=True)
    Carpeta = models.IntegerField(null=True, blank=True)
    DescripcionUnidadDocumental = models.TextField(null=True, blank=True)
    NoFolioInicio = models.IntegerField(null=True, blank=True)
    NoFolioFin = models.IntegerField(null=True, blank=True)
    paginas = models.IntegerField()
    Soporte = models.CharField(max_length=50, null=True, blank=True)
    FechaIngreso = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'IndiceTemp'
        ordering = ['id2']

    def __str__(self):
        return f"IndiceTemp {self.id2} - Caja {self.Caja}, Carpeta {self.Carpeta}"
    
class Serie(models.Model):
    nombre = models.CharField(max_length=255)

    def __str__(self):
        return self.nombre



