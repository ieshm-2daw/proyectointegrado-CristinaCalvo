from django.contrib import admin
from .models import Usuario, Servicio, Compra, Ubicacion, Room, Mensaje, Reporte
from django.contrib.auth.admin import UserAdmin

class CustomUserAdmin(UserAdmin):
    model = Usuario
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('saldo', 'baneado')}), 
    )

    add_fieldsets = UserAdmin.add_fieldsets + (
        (None, {'fields': ('saldo',)}),  # Mantén el formulario de creación de usuario igual
    )

    list_display = ('username', 'email', 'baneado')  # Muestra la información de baneo en la lista de usuarios
    list_filter = ('baneado',)  # Agrega un filtro para baneado en el panel de administrador
    
admin.site.register(Usuario, CustomUserAdmin)
admin.site.register(Servicio)
admin.site.register(Compra)
admin.site.register(Ubicacion)
admin.site.register(Room)
admin.site.register(Mensaje)
admin.site.register(Reporte)
