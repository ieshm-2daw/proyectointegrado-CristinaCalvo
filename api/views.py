from django.shortcuts import render
from .serializers import ServicioSerializers
from rest_framework import viewsets, permissions
from SkillsHub.models import Servicio

class ServicioViewSet (viewsets.ModelViewSet):
    queryset = Servicio.objects.all()
    serializer_class = ServicioSerializers
    permissions_classes = [permissions.AllowAny]

