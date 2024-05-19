from django.urls import path
from . import views
from .views import Servicios, ServicioNuevo, Detalles, Actualiza, Borra, RealizarCompra, Valoraciones, PerfilUsuario
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required


urlpatterns = [
    path('', Servicios.as_view(), name='servicios'),
    path('nuevo_servicio/', login_required(ServicioNuevo.as_view()), name='nuevo_servicio'),
    path('detalles/<int:pk>/', Detalles.as_view(), name='detalles'),
    path('actualiza/<int:pk>/', login_required(Actualiza.as_view()), name='actualiza'),
    path('borra/<int:pk>/', login_required(Borra.as_view()), name='borra'),

    path('register/', views.register, name='register'),

    path('checkout/<int:pk>/', login_required(RealizarCompra.as_view()), name='checkout'),

    path('valoraciones/<int:pk>/', login_required(Valoraciones.as_view()), name='valoraciones'),

    path('perfil_usuario/<int:pk>/', login_required(PerfilUsuario.as_view()), name='perfil_usuario'),

    path('configura_perfil/', login_required(views.configura_perfil), name='configura_perfil'),

    path('buscar_usuario/', views.buscar_usuario, name='buscar_usuario'),

    path('gestion/', views.gestion, name='gestion'),
    path('top-vendedores/', staff_member_required(views.top_vendedores), name='top_vendedores'),
    path('top-compradores/', staff_member_required(views.top_compradores), name='top_compradores'),
    path('lista-reportes/', views.lista_reportes, name='lista_reportes'),

    path('rooms',  login_required(views.room), name="rooms"),

    path('chat/<slug:slug>/',  login_required(views.chatPage), name="chat"),

    path('iniciar_chat/<int:user_id>/', login_required(views.iniciar_chat), name='iniciar_chat'),

    path('reportar/<int:user_id>/', login_required(views.reportar_usuario), name='reportar'),
    path('error/', views.error, name='error'),
    
]