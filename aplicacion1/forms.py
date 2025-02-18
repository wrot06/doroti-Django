from django import forms
from .models import Carpeta



class CarpetaForm(forms.ModelForm):
    class Meta:
        model = Carpeta
        fields = ['caja', 'carpeta']

