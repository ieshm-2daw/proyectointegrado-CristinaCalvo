from django.shortcuts import render,  get_object_or_404, redirect
from .models import Usuario, Compra, Servicio, Room, Mensaje, Reporte, Ubicacion, UsuarioInsignia, Insignia
from django.views import View
from django.views.generic import ListView, DetailView
from .forms import ServicioForm, ValoracionForm, RegisterForm, PerfilForm, FiltroCategoria, FiltroUbicacion, ReporteForm
from django.views.generic.edit import UpdateView, CreateView, DeleteView
from django.urls import reverse_lazy
from django.contrib import messages
from django.utils import timezone
from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse
from django.db import models
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, JsonResponse
from django.db.models import Q


# Create your views here.

class Servicios(ListView):
    template_name = 'Proyecto/servicios.html'
    model = Servicio
    form_class_categoria = FiltroCategoria
    form_class_ubicacion = FiltroUbicacion

    def get_queryset(self):
        queryset = Servicio.objects.filter(activo=True)
        categoria = self.request.GET.get('categorias', None)
        ubicacion = self.request.GET.get('ubicacion', None)  # Valor de ubicacion

        if categoria:
            queryset = queryset.filter(categoria=categoria)

        if ubicacion:
            queryset = queryset.filter(ubicacion=ubicacion)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form_categoria'] = self.form_class_categoria(initial={'categorias': self.request.GET.get('categorias', None)})
        context['form_ubicacion'] = self.form_class_ubicacion(initial={'ubicacion': self.request.GET.get('ubicacion', None)}) 
        return context

class ServicioNuevo(CreateView):
    model = Servicio
    form_class = ServicioForm
    template_name = 'Proyecto/nuevo_servicio.html'
    success_url = reverse_lazy('servicios')

    def form_valid(self, form): 
        form.instance.usuario = self.request.user
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['ubicaciones'] = Ubicacion.objects.all()  # Obtener todas las ubicaciones disponibles
        return context

class Detalles(DetailView):
    model = Servicio
    template_name = 'Proyecto/detalles.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
       
        if self.request.user.is_authenticated: #Verifica si el usuario está autenticado
            servicio = self.get_object()
            existeValoracion = False

            compras = servicio.compra_set.all() #Comprueba todas las compras que hay de ese servicio
            for compra in compras:
                if compra.valoracion:
                    existeValoracion = True
                    break

            #Vemos las compras que tiene el usuario actual y si hay alguna de este servicio
            compras_usuario = Compra.objects.filter(usuario_comprador=self.request.user, servicio=servicio)
            ha_realizado_compra = compras_usuario.exists()

            context['ha_realizado_compra'] = ha_realizado_compra
            context['existeValoracion'] = existeValoracion  # Para mostrar todas las valoraciones
        return context


class Actualiza(UpdateView):
    model = Servicio
    form_class = ServicioForm
    template_name = 'Proyecto/actualiza.html'
    success_url = reverse_lazy('servicios')

    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user
        if user.is_authenticated:
            if user.is_superuser:
                return queryset.all() # Si el usuario es administrador, devuelve todos los objetos
            else:
                return queryset.filter(usuario=user)  # Si el usuario no es administrador, filtra por el usuario actual
        else:
            return queryset.none() # Si el usuario no está autenticado, devuelve un queryset vacío

class Borra(DeleteView):
    model = Servicio
    template_name = 'Proyecto/borra.html'
    success_url = reverse_lazy('servicios')

    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user
        if user.is_authenticated:
            if user.is_superuser:
                return queryset.all() # Si el usuario es administrador, devuelve todos los objetos
            else:
                return queryset.filter(usuario=user)  # Si el usuario no es administrador, filtra por el usuario actual
        else:
            return queryset.none() # Si el usuario no está autenticado, devuelve un queryset vacío

class RealizarCompra(View): #Como tanto fecha como fecha_limite de valoracion son automaticas desde el modelo no hay que calcular nada
    template_name = "Proyecto/checkout.html"

    def get(self, request, pk):
        servicio = get_object_or_404(Servicio, pk=pk)
        return render(request, self.template_name, {'servicio': servicio})

    def post(self, request, pk):
        servicio = Servicio.objects.get(pk=pk)
        usuario_comprador = request.user
        usuario_vendedor = servicio.usuario

        # El mismo usuario no puede comprarse a si mismo SE PODRIA QUITAR EL "COMPRAR DIRECTAMENTE"
        if servicio.usuario == usuario_comprador:
            messages.error(request, 'No puedes comprar tu propio servicio.')
            return redirect('detalles', pk=pk) #detalles del servicio

        # Si el servicio esta desactivado que no pueda comprarlo SE PODRIA QUITAR EL "COMPRAR DIRECTAMENTE"
        if not servicio.activo:
            messages.error(request, 'Este servicio está desactivado y no se puede comprar.')
            return redirect('detalles', pk=pk) #detalles del servicio

        # Comprobar que tiene suficiente saldo
        if usuario_comprador.saldo < servicio.precio:
            messages.error(request, 'No tienes suficiente saldo para realizar esta compra.')
            return redirect('detalles', pk=pk) #detalles del servicio

        compra = Compra(usuario_comprador=usuario_comprador, servicio=servicio, usuario_vendedor=usuario_vendedor)
        compra.save()

        usuario_comprador.saldo -= servicio.precio
        usuario_comprador.save()
        usuario_vendedor.saldo += servicio.precio
        usuario_vendedor.save()

        messages.success(request, '¡La compra se ha realizado con éxito!, puedes dejar una valoración después de una semana')
        return redirect('servicios')


class Valoraciones(UpdateView):
    model = Compra
    form_class = ValoracionForm
    template_name = 'Proyecto/valoraciones.html'
    success_url = reverse_lazy('detalles')

    def get(self, request, pk):
        servicio = get_object_or_404(Servicio, pk=pk)
        usuario_actual = request.user
        compra = Compra.objects.filter(servicio=servicio, usuario_comprador=usuario_actual).first()
        if compra:
            if compra.fecha > timezone.now():
                messages.error(request, "La fecha límite para valorar este servicio aún no ha pasado.")
                return redirect('detalles', pk=pk)
            form = ValoracionForm(instance=compra)
            return render(request, self.template_name, {'servicio': servicio, 'compra': compra, 'form': form})
        else:
            return redirect('detalles', pk=pk)

    def post(self, request, pk):
        servicio = get_object_or_404(Servicio, pk=pk)
        usuario_actual = request.user
        compra = Compra.objects.filter(servicio=servicio, usuario_comprador=usuario_actual).first()
        if compra and compra.fecha <= timezone.now():
            form = self.form_class(request.POST, instance=compra)
            if form.is_valid():
                form.save()
                return redirect('detalles', pk=pk)
        return redirect('detalles', pk=pk)



def register(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Registrado con éxito")
            return redirect("/")
    else:
        form = RegisterForm()

    return render(request, "registration/register.html", {"form": form})


def configura_perfil(request):
    perfil_usuario = request.user

    if request.user == perfil_usuario:
        if request.method == 'POST':
            form = PerfilForm(request.POST, request.FILES, instance=request.user)
            if form.is_valid():
                pk = request.user.pk
                form.save()
                return redirect('perfil_usuario', pk=pk)  
        else:
            form = PerfilForm(instance=request.user)
        return render(request, 'Proyecto/configura_perfil.html', {'form': form})
    else:
        return render(request, 'Proyecto/perfil_usuario.html')

class PerfilUsuario(LoginRequiredMixin, View):
    template_name = 'Proyecto/perfil_usuario.html'

    def get(self, request, pk):
        usuario = get_object_or_404(Usuario, pk=pk)
        servicios = Servicio.objects.filter(usuario=usuario)
        compras_realizadas = Compra.objects.filter(usuario_comprador=usuario)

        if request.user == usuario:
            permitir_configuracion = True
            compras_realizadas = Compra.objects.filter(usuario_comprador=usuario)
        else:
            permitir_configuracion = False
            compras_realizadas = None

        seguidores = usuario.usuarios_seguidores.all()
        seguidos = usuario.usuarios_seguidos.all()

        context = {
            'usuario': usuario,
            'servicios': servicios,
            'compras_realizadas': compras_realizadas,
            'permitir_configuracion': permitir_configuracion,
            'seguidores': seguidores,
            'seguidos': seguidos,
        }
        return render(request, self.template_name, context)
    
def seguir_usuario(request, pk):
    usuario_a_seguir = get_object_or_404(Usuario, pk=pk)
    request.user.usuarios_seguidos.add(usuario_a_seguir)
    usuario_a_seguir.usuarios_seguidores.add(request.user)
    return redirect('perfil_usuario', pk=pk)

def dejar_de_seguir_usuario(request, pk):
    usuario_a_dejar_de_seguir = get_object_or_404(Usuario, pk=pk)
    request.user.usuarios_seguidos.remove(usuario_a_dejar_de_seguir)
    usuario_a_dejar_de_seguir.usuarios_seguidores.remove(request.user)
    return redirect('perfil_usuario', pk=pk)

def lista_seguidores(request, pk):
    usuario = get_object_or_404(Usuario, pk=pk)
    seguidores = usuario.usuarios_seguidores.all()
    return render(request, 'Proyecto/seguidores.html', {'usuario': usuario, 'seguidores': seguidores})

def lista_seguidos(request, pk):
    usuario = get_object_or_404(Usuario, pk=pk)
    seguidos= usuario.usuarios_seguidos.all()
    return render(request, 'Proyecto/seguidos.html', {'usuario': usuario, 'seguidos': seguidos})
    

def buscar_usuario(request):
    nombre_usuario = request.GET.get('nombre_usuario')

    if nombre_usuario:
        try:
            usuario = Usuario.objects.get(username=nombre_usuario)
            return redirect('perfil_usuario', pk=usuario.pk)
        except Usuario.DoesNotExist:
            messages.error(request, "Ese usuario no existe")
    return redirect('servicios')  


# GESTIÓN
def top_vendedores(request):
    top_vendedores = Usuario.objects.annotate(num_ventas=models.Count('ventas_realizadas')).order_by('-num_ventas')[:10]
    return render(request, 'Proyecto/top_vendedores.html', {'top_vendedores': top_vendedores})

def top_compradores(request):
    top_compradores = Usuario.objects.annotate(num_compras=models.Count('compras_realizadas')).order_by('-num_compras')[:10]
    return render(request, 'Proyecto/top_compradores.html', {'top_compradores': top_compradores})


# MENSAJERIA
def room(request):
    current_user = request.user
    rooms = Room.objects.filter(usuarios=current_user) #que solo te salgan los chats de el usuario actual
    for room in rooms:
        otro = room.usuarios.exclude(username=current_user.username).first()
        room.otro_usuario = otro.username if otro else "Otro" #para asignar nombres de la sala con otro usuario
    return render(request, "Proyecto/rooms.html", {'rooms': rooms})


def chatPage(request, slug):
    room = get_object_or_404(Room, slug=slug)
    mensajes = Mensaje.objects.filter(room=room)
    
    current_user = request.user
    otro = room.usuarios.exclude(username=current_user.username).first() #Para obtener al otro usuario
    
    contexto = {
        "room": room,
        "mensajes": mensajes,
        "otro": otro,
    }

    return render(request, "Proyecto/chat.html", contexto)


def iniciar_chat(request, user_id): #para habalr con el usuario actual al de pfu
    current_user = request.user
    print(current_user)
   

    destinatario = get_object_or_404(Usuario, id=user_id)
    print(destinatario.username)

    
    if current_user.id == destinatario.id:
        return HttpResponseRedirect(reverse('rooms'))  

    
    chat_room_name = f"{min(current_user.username, destinatario.username)}_{max(current_user.username, destinatario.username)}"

    # Verifica si ya existe una sala para estos dos usuarios
    existing_room = Room.objects.filter(slug=chat_room_name).first()

    if existing_room:
       
        return HttpResponseRedirect(reverse('chat', args=[existing_room.slug]))

    
    new_room = Room.objects.create(
        name=chat_room_name,
        slug=chat_room_name
    )

    new_room.usuarios.add(current_user, destinatario) #Adjudicamos la sala a los usuarios

    return HttpResponseRedirect(reverse('chat', args=[new_room.slug]))


#BANEO DE USUARIO
def banear_usuario(usuario):
    usuario.baneado = True
    usuario.save()

def desbanear_usuario(usuario):
    usuario.baneado = False
    usuario.save()

def lista_usuarios(request):
    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        action = request.POST.get('action')
        usuario = get_object_or_404(Usuario, id=user_id)
        if action == 'banear':
            banear_usuario(usuario)  
        elif action == 'desbanear':
            desbanear_usuario(usuario)  # Desbanea al usuario
        return redirect('lista_usuarios')  # Redirige a la lista de usuarios después de banear/desbanear
    
    usuarios = Usuario.objects.all()  # Obtén todos los usuarios
    return render(request, 'Proyecto/lista_usuarios.html', {'usuarios': usuarios})

def reportar_usuario(request, user_id):
    usuario_reportado = get_object_or_404(Usuario, pk=user_id)
    if request.method == 'POST':
        form = ReporteForm(request.POST)
        if form.is_valid():
            reporte = form.save(commit=False)
            reporte.reportador = request.user
            reporte.usuario_reportado = usuario_reportado
            reporte.save()
            return redirect('/')
    else:
        form = ReporteForm()
    return render(request, 'Proyecto/reportar.html', {'form': form, 'usuario_reportado': usuario_reportado})


def gestion(request):
    return render(request, 'Proyecto/gestion.html')


def lista_reportes(request):
    reportes = Reporte.objects.all()
    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        accion = request.POST.get('accion')
        if accion == 'banear':
            usuario = Usuario.objects.get(id=user_id)
            usuario.baneado = True
            usuario.save()
        elif accion == 'desbanear':
            usuario = Usuario.objects.get(id=user_id)
            usuario.baneado = False
            usuario.save()
        elif accion == 'eliminar_reporte':
            reporte_id = request.POST.get('reporte_id')
            Reporte.objects.get(id=reporte_id).delete()
        return redirect('lista_reportes')
    return render(request, 'Proyecto/lista_reportes.html', {'reportes': reportes})


class BanMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

       
        if request.user.is_authenticated and request.user.baneado:
            return redirect(reverse('error'))

        return response

def error(request):
    return render(request, 'Proyecto/error.html')


def lista_compras(request):
    compras = Compra.objects.filter(usuario_comprador=request.user).order_by('-fecha')
    return render(request, 'Proyecto/lista_compras.html', {'compras': compras})


def lista_insignias(request):
    usuario = request.user
    
    insignias = [
        {
            "nombre": "Dos compras en un día",
            "descripcion": "Te han comprado dos veces en el mismo día.",
            "icono": "insignias/dos_compras_dia.png",
            "condicion": lambda u: Compra.objects.filter(usuario_vendedor=u, fecha__date=timezone.now().date()).count() >= 2
        },
        {
            "nombre": "Primera venta",
            "descripcion": "Has realizado tu primera venta.",
            "icono": "insignias/primera_venta.png",
            "condicion": lambda u: Compra.objects.filter(usuario_vendedor=u).exists()
        },
        {
            "nombre": "Diez servicios diferentes vendidos",
            "descripcion": "Has vendido diez servicios diferentes.",
            "icono": "insignias/diez_servicios_vendidos.png",
            "condicion": lambda u: Compra.objects.filter(usuario_vendedor=u).values('servicio').distinct().count() >= 10
        },
        {
            "nombre": "Primera valoración de 5 estrellas",
            "descripcion": "Has recibido tu primera valoración de 5 estrellas.",
            "icono": "insignias/primera_valoracion_cinco_estrellas.png",
            "condicion": lambda u: Compra.objects.filter(usuario_vendedor=u, valoracion=5).exists()
        },
        {
            "nombre": "Primera compra",
            "descripcion": "Has realizado tu primera compra.",
            "icono": "insignias/primera_compra.png",
            "condicion": lambda u: Compra.objects.filter(usuario_comprador=u).exists()
        },
    ]

    # Asignar insignias al usuario
    for insignia_data in insignias:
        if insignia_data["condicion"](usuario):
            insignia, created = Insignia.objects.get_or_create(
                nombre=insignia_data["nombre"],
                defaults={
                    "descripcion": insignia_data["descripcion"],
                    "icono": insignia_data["icono"]
                }
            )
            UsuarioInsignia.objects.get_or_create(usuario=usuario, insignia=insignia, defaults={"desbloqueada": True})

    insignias_desbloqueadas = UsuarioInsignia.objects.filter(usuario=usuario, desbloqueada=True)
    
    return render(request, 'Proyecto/lista_insignias.html', {'insignias': insignias_desbloqueadas})

def seleccionar_insignia_perfil(request, insignia_id):
    usuario = request.user
    insignia = get_object_or_404(UsuarioInsignia, id=insignia_id, usuario=usuario)
    
    usuario.insignia_perfil = insignia
    usuario.save()
    
    messages.success(request, 'Insignia seleccionada para mostrar en tu perfil.')
    return redirect(reverse('perfil_usuario', kwargs={'pk': usuario.pk}))