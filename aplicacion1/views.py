from django.shortcuts import render, redirect, get_list_or_404
from django.contrib import messages
from django.http import JsonResponse
from django.views import View
from django.views.decorators.http import require_POST, require_GET
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction, connection
from django.db.models import Max

import json
import urllib.parse

from django import forms
from .forms import CarpetaForm
from .models import Carpeta, IndiceTemp, Serie

from .forms import CarpetaForm
from .models import Carpeta, IndiceTemp, Serie, Subs

from django.db import connection
import json
from django.http import JsonResponse

from .models import Serie
from django.http import JsonResponse
from .models import Subs  # Asegúrate de que el modelo esté bien importado

from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_list_or_404
from .models import Subs

from django.shortcuts import render

@require_POST
def obtener_Subs_view(request):
    # Recibir el ID de la serie desde POST
    serie_id = request.POST.get("serie_id")
    
    if not serie_id:
        return JsonResponse({"error": "No se proporcionó una serie"}, status=400)
    
    try:
        # Obtener el objeto Serie usando el ID
        serie = get_object_or_404(Serie, pk=serie_id)
        
        # Filtrar las subseries usando el nombre de la serie (campo 'serie_nombre')
        subseries = Subs.objects.filter(serie_nombre=serie.nombre).values("id", "Subs")
        
        # Retornar los datos en un JSON bajo la clave "subseries"
        return JsonResponse({"subseries": list(subseries)})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)



def indice_view(request):
    # Si se envían nuevos datos por POST, se actualizan en la sesión.
    if request.method == "POST":
        caja = request.POST.get('caja')
        carpeta = request.POST.get('carpeta')
        if caja and carpeta:
            request.session['caja'] = caja
            request.session['carpeta'] = carpeta
        else:
            # Si no vienen datos, se intenta obtener de la sesión.
            caja = request.session.get('caja')
            carpeta = request.session.get('carpeta')
    else:
        # En GET se obtienen de la sesión.
        caja = request.session.get('caja')
        carpeta = request.session.get('carpeta')

    # Si no hay caja o carpeta definidos, redirige o muestra un error.
    if not caja or not carpeta:
        # Puedes redirigir a una página de selección o al login
        return redirect('login')

    # Convertir a enteros (si es necesario)
    try:
        caja = int(caja)
        carpeta = int(carpeta)
    except ValueError:
        return redirect('login')

    print(f"DEBUG Indice - Caja en sesión: {request.session.get('caja')}")
    print(f"DEBUG Indice - Carpeta en sesión: {request.session.get('carpeta')}")

    # Consulta: obtener solo los capítulos correspondientes a la caja y carpeta actual.
    capitulos = IndiceTemp.objects.filter(Caja=caja, Carpeta=carpeta).order_by('id2')

    # Calcular la última página a partir del valor máximo de NoFolioFin
    ultimaPagina = 0
    for cap in capitulos:
        if cap.NoFolioFin and cap.NoFolioFin > ultimaPagina:
            ultimaPagina = cap.NoFolioFin

    # Obtener las etiquetas (Series) si se utilizan
    etiquetas = Serie.objects.all().order_by('nombre')

    context = {
        'caja': caja,
        'carpeta': carpeta,
        'capitulos': capitulos,
        'ultimaPagina': ultimaPagina,
        'etiquetas': etiquetas,
    }
    return render(request, 'indice.html', context)


from aplicacion1.models import Serie  # Asegúrate de importar el modelo

def tcarpeta_view(request):
    # Intentar obtener los valores desde el formulario
    caja = request.POST.get("caja")
    carpeta = request.POST.get("carpeta")

    # Si no vienen en POST, intentar recuperarlos desde la sesión
    if not caja:
        caja = request.session.get("caja")
    if not carpeta:
        carpeta = request.session.get("carpeta")

    # Verificar si los datos existen, sino redirigir a índice
    if not caja or not carpeta:
        print("DEBUG tcarpeta: No se encontraron datos de caja y carpeta en POST ni en la sesión")
        return redirect("indice")  # Asegúrate de que esta URL esté bien definida

    print(f"DEBUG tcarpeta - Caja: {caja}")
    print(f"DEBUG tcarpeta - Carpeta: {carpeta}")

    # Obtener las etiquetas (series) desde la base de datos
    etiquetas = Serie.objects.all().order_by("nombre")

    context = {
        "caja": caja,
        "carpeta": carpeta,
        "etiquetas": etiquetas,  # Pasar etiquetas al template
    }
    return render(request, "tcarpeta.html", context)






class CarpetaForm(forms.Form):
    caja = forms.IntegerField(widget=forms.HiddenInput())
    carpeta = forms.IntegerField(widget=forms.HiddenInput())
    serie = forms.ChoiceField(choices=[], required=True, widget=forms.Select(attrs={'class': 'form-control form-control-sm'}))
    Subs = forms.ChoiceField(choices=[], required=False, widget=forms.Select(attrs={'class': 'form-control form-control-sm'}))
    tituloCarpeta = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'maxlength': 56}), required=True)
    fechaInicial = forms.DateField(widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}), required=True)
    fechaFinal = forms.DateField(widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}), required=True)
    folios = forms.IntegerField(widget=forms.HiddenInput(), required=False)

class CarpetaView(View):
    template_name = 'tcarpeta.html'

    def get_series(self):
        with connection.cursor() as cursor:
            cursor.execute("SELECT id, nombre FROM Serie ORDER BY nombre ASC")
            series = cursor.fetchall()
        return [(s[1], s[1]) for s in series]

    def get(self, request):
        caja = request.GET.get('caja')
        carpeta = request.GET.get('carpeta')

        with connection.cursor() as cursor:
            cursor.execute("SELECT MAX(NoFolioFin) FROM IndiceTemp WHERE caja = %s AND carpeta = %s", [caja, carpeta])
            ultima_pagina = cursor.fetchone()[0] or 0

        form = CarpetaForm(initial={'caja': caja, 'carpeta': carpeta, 'folios': ultima_pagina})
        form.fields['serie'].choices = self.get_series()

        # Obtener las subseries desde la base de datos
        subseries = Subs.objects.all().order_by('Subs')

        return render(request, self.template_name, {
            'form': form,
            'caja': caja,
            'carpeta': carpeta,
            'ultima_pagina': ultima_pagina,
            'subseries': subseries  # Pasamos las subseries al contexto
        })



@require_GET
def obtener_capitulos_view(request):
    try:
        caja = request.GET.get('caja')
        carpeta = request.GET.get('carpeta')
        if caja is None or carpeta is None:
            return JsonResponse({'status': 'error', 'message': 'Parámetros inválidos.'}, status=400)
        
        caja = int(caja)
        carpeta = int(carpeta)
        
        capitulos = IndiceTemp.objects.filter(Caja=caja, Carpeta=carpeta).order_by('id2')
        
        data = []
        for cap in capitulos:
            data.append({
                'id': cap.id2,
                'titulo': cap.DescripcionUnidadDocumental,
                'paginas': cap.paginas,
                'paginaInicio': cap.NoFolioInicio,
                'paginaFinal': cap.NoFolioFin,
            })
        return JsonResponse(data, safe=False)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


@require_POST
def eliminar_capitulo_view(request):
    try:
        # Obtener y validar parámetros
        id_capitulo = request.POST.get('id')
        caja = request.POST.get('caja')
        carpeta = request.POST.get('carpeta')
        
        if not (id_capitulo and caja and carpeta):
            return JsonResponse({'status': 'error', 'message': 'Faltan parámetros.'})
        
        id_capitulo = int(id_capitulo)
        caja = int(caja)
        carpeta = int(carpeta)
        
        # Iniciar la transacción
        with transaction.atomic():
            # Paso 1: Eliminar el capítulo
            deleted, _ = IndiceTemp.objects.filter(Caja=caja, Carpeta=carpeta, id2=id_capitulo).delete()
            if deleted == 0:
                return JsonResponse({'status': 'error', 'message': 'No se encontró el capítulo.'})
            
            # Paso 2: Obtener los capítulos restantes ordenados por id2 (ascendente)
            capitulos = list(IndiceTemp.objects.filter(Caja=caja, Carpeta=carpeta).order_by('id2'))
            
            # Paso 3: Recalcular las páginas y actualizar cada capítulo
            siguiente_pagina = 1
            for index, capitulo in enumerate(capitulos):
                pagina_inicio = siguiente_pagina
                # Se asume que el campo 'paginas' contiene el número de páginas del capítulo
                pagina_final = pagina_inicio + capitulo.paginas - 1
                nuevo_id2 = index + 1
                
                # Actualizar el registro para el capítulo actual
                IndiceTemp.objects.filter(pk=capitulo.pk).update(
                    NoFolioInicio=pagina_inicio,
                    NoFolioFin=pagina_final,
                    id2=nuevo_id2
                )
                
                siguiente_pagina = pagina_final + 1
            
            # La transacción se confirma automáticamente al salir del bloque with.
        
        return JsonResponse({
            'status': 'success',
            'message': 'Capítulo eliminado y páginas recalculadas correctamente'
        })
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})


@require_GET
def actualizar_orden_view(request):
    data = request.GET.get('data')
    if not data:
        return JsonResponse({'status': 'error', 'message': 'No se recibieron datos'})
    
    try:
        # Decodificar el parámetro (si está URL-encoded)
        decoded_data = urllib.parse.unquote(data)
        json_data = json.loads(decoded_data)
        
        cambios = json_data.get('cambios', [])
        caja = json_data.get('caja')
        carpeta = json_data.get('carpeta')
        
        if not (caja and carpeta):
            return JsonResponse({'status': 'error', 'message': 'Caja y Carpeta son requeridos.'})
        
        # Iterar sobre cada cambio y actualizar el registro correspondiente
        for capitulo in cambios:
            inicio = capitulo.get('inicio')
            fin = capitulo.get('fin')
            titulo = capitulo.get('titulo')
            paginas = capitulo.get('paginas')
            id2 = capitulo.get('id')
            
            # Actualizar el registro filtrando por Caja, Carpeta y el identificador secundario id2
            updated = IndiceTemp.objects.filter(Caja=caja, Carpeta=carpeta, id2=id2).update(
                NoFolioInicio=inicio,
                NoFolioFin=fin,
                DescripcionUnidadDocumental=titulo,
                paginas=paginas
            )
            if updated == 0:
                # Si no se actualizó ningún registro, podemos devolver un error
                return JsonResponse({
                    'status': 'error', 
                    'message': f'No se encontró el capítulo con id2 {id2} para Caja {caja} y Carpeta {carpeta}.'
                })
        
        return JsonResponse({'status': 'success', 'message': 'Actualización exitosa'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})

def login_view(request):
    error = None
    if request.method == "POST":
        password = request.POST.get("password")
        correct_password = "Rene"  # Contraseña fija por ahora

        if password == correct_password:
            request.session["authenticated"] = True
            return redirect("index")  # Redirige a la página protegida
        else:
            error = "Contraseña incorrecta."

    return render(request, "login.html", {"error": error})

def logout_view(request):
    request.session.flush()
    return redirect("login")

def index_view(request):
    # Filtra solo las carpetas activas (estado 'A') y las ordena por caja
    carpetas = Carpeta.objects.filter(estado='A').order_by('caja')
    return render(request, "index.html", {"carpetas": carpetas})

def buscador_view(request):
    return render(request, "buscador.html")

def agregar_carpeta_view(request):
    if request.method == "POST":
        form = CarpetaForm(request.POST)
        if form.is_valid():
            form.save()  # Se guardan caja y carpeta; los demás se completan con default
            messages.success(request, "Carpeta agregada exitosamente.")
            return redirect('index')
        else:
            messages.error(request, "Por favor corrige los errores.")
    else:
        form = CarpetaForm()
    return render(request, "agregar_carpeta.html", {'form': form})

@csrf_exempt  # Puedes quitarlo si envías el token CSRF desde el cliente
@require_POST
def agregar_capitulo_view(request):
    try:
        # Extraer y validar los datos del POST
        caja = int(request.POST.get('caja', 0))
        carpeta = int(request.POST.get('carpeta', 0))
        titulo = request.POST.get('titulo', '').strip()
        paginaFinal = int(request.POST.get('paginaFinal', 0))

        if not caja or not carpeta or not titulo or not paginaFinal:
            raise Exception("Todos los campos son obligatorios y deben ser válidos.")

        # Obtener la última página final registrada para esta caja y carpeta
        last_page = IndiceTemp.objects.filter(Caja=caja, Carpeta=carpeta).aggregate(last_page=Max('NoFolioFin'))['last_page'] or 0
        paginaInicio = last_page + 1

        if paginaFinal < paginaInicio:
            raise Exception(f"La página final debe ser mayor o igual que {paginaInicio}.")

        paginas = paginaFinal - paginaInicio + 1

        # Obtener el último id2 registrado para esta caja y carpeta
        last_id2 = IndiceTemp.objects.filter(Caja=caja, Carpeta=carpeta).aggregate(last_id=Max('id2'))['last_id'] or 0
        id2 = last_id2 + 1

        # Crear el nuevo registro en IndiceTemp
        nuevo_capitulo = IndiceTemp.objects.create(
            id2=id2,
            Caja=caja,
            Carpeta=carpeta,
            DescripcionUnidadDocumental=titulo,
            NoFolioInicio=paginaInicio,
            NoFolioFin=paginaFinal,
            paginas=paginas
        )

        data = {
            'status': 'success',
            'capitulo': {
                'id': nuevo_capitulo.id2,
                'titulo': nuevo_capitulo.DescripcionUnidadDocumental,
                'pagina_inicio': nuevo_capitulo.NoFolioInicio,
                'pagina_final': nuevo_capitulo.NoFolioFin,
                'num_paginas': nuevo_capitulo.paginas,
            }
        }
        return JsonResponse(data)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})