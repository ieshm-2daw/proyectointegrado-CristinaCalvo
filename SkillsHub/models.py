from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone

class Usuario(AbstractUser):
    nombre = models.CharField(max_length=100) 
    saldo = models.DecimalField(max_digits=10, decimal_places=2, default=0, null=True)
    avatar = models.ImageField(upload_to='avatars/', default='avatars/perfil.png') 
    comentario = models.TextField(blank=True, null=True)
    baneado = models.BooleanField(default=False) 
    

    def __str__(self):
        return self.username

class Reporte(models.Model):
    usuario_reportado = models.ForeignKey(Usuario, related_name='reportes_recibidos', on_delete=models.CASCADE)
    reportador = models.ForeignKey(Usuario, related_name='reportes_enviados', on_delete=models.CASCADE)
    motivo = models.TextField()
    fecha = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Reporte de {self.usuario_reportado} por {self.reportador} el {self.fecha}"
    

class Ubicacion(models.Model):
    nombre = models.CharField(max_length=100)

    def __str__(self):
        return self.nombre

class Servicio(models.Model):
    nombre = models.CharField(max_length=100)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    descripcion = models.TextField()
    ubicacion = models.ForeignKey(Ubicacion, on_delete=models.CASCADE)
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    activo = models.BooleanField(default=True)
    categoria = models.CharField(max_length=255, blank=True, null=True) 
    imagen = models.ImageField(upload_to='servicio/', blank=False, default='servicio/blanco.jpeg')

    def __str__(self):
        return(self.nombre)

class Compra(models.Model):
    usuario_comprador = models.ForeignKey(Usuario, related_name='compras_realizadas', on_delete=models.CASCADE)
    servicio = models.ForeignKey(Servicio, on_delete=models.CASCADE)
    fecha = models.DateTimeField(default=timezone.now) #Hacemos que automaticamente se ponga como fecha y hora actual
    valoracion = models.TextField(blank=True, null=True)
    puntuacion = models.IntegerField(default=0, choices=[(i, i) for i in range(6)]) #Que el rango de puntuacion sea del 0-5
    usuario_vendedor = models.ForeignKey(Usuario, related_name='ventas_realizadas', on_delete=models.CASCADE) 
    #Se pone related_name ya que no se puede poner dos FK iguales sobre el mismo modelo ya que chocan, asi se distinguen

class Meta:
    unique_together = ('usuario', 'servicio', 'fecha')

class Room(models.Model):
    name=models.CharField(max_length=20)
    slug = models.SlugField(max_length=20, unique=True)  # id sala unico
    usuarios = models.ManyToManyField(Usuario, related_name='rooms')  # para adjudicar sala a los usuarios y poder filtrar 

    def __str__(self):
        return(self.name)

class Mensaje(models.Model):
    content=models.TextField()
    usuario=models.ForeignKey(Usuario,on_delete=models.CASCADE)
    room=models.ForeignKey(Room,on_delete=models.CASCADE)
    created_on=models.DateTimeField(auto_now_add=True)