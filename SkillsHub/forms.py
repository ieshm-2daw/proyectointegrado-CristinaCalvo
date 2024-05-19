from django import forms
from .models import Servicio, Usuario, Compra, Ubicacion, Reporte
from django.contrib.auth.forms import UserCreationForm

class ServicioForm(forms.ModelForm):
    class Meta:
      model = Servicio
      fields = ['nombre', 'precio', 'descripcion', 'categoria','ubicacion', 'activo', 'imagen']

class ValoracionForm(forms.ModelForm):
  class Meta:
    model = Compra
    fields = ['valoracion', 'puntuacion']

class RegisterForm(UserCreationForm):
   email = forms.EmailField()
   class Meta:
      model = Usuario
      fields = ["username", "email", "password1", "password2"]

class PerfilForm(forms.ModelForm):
    class Meta:
      model = Usuario
      fields = ['saldo', 'comentario', 'avatar']
      
class FiltroCategoria(forms.Form):
    categorias = forms.ChoiceField(choices=[], required=False, label='Categoría')

    def __init__(self, *args, **kwargs):
        super(FiltroCategoria, self).__init__(*args, **kwargs)
        categorias = Servicio.objects.values_list('categoria', flat=True).distinct()
        choices = [(c, c) for c in categorias]
        choices.insert(0, ('', 'Categoría'))
        self.fields['categorias'].choices = choices


class FiltroUbicacion(forms.Form):
    ubicacion = forms.ModelChoiceField(queryset=Ubicacion.objects.all(), empty_label="Ubicación", required=False)


class ReporteForm(forms.ModelForm):
    class Meta:
        model = Reporte
        fields = ['motivo']