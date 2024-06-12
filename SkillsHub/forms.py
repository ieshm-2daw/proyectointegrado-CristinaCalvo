from django import forms
from .models import Servicio, Usuario, Compra, Ubicacion, Reporte, Categoria
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
    categoria = forms.ModelChoiceField(queryset=Categoria.objects.all(), empty_label="Categoría", required=False)

class FiltroUbicacion(forms.Form):
    ubicacion = forms.ModelChoiceField(queryset=Ubicacion.objects.all(), empty_label="Ubicación", required=False)


class ReporteForm(forms.ModelForm):
    class Meta:
        model = Reporte
        fields = ['motivo']