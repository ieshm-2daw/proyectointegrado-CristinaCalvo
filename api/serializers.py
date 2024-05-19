from rest_framework import serializers
from SkillsHub.models import Servicio

class ServicioSerializers(serializers.ModelSerializer):
    class Meta:
        model = Servicio
        fields = ('nombre','precio','descripcion','ubicacion','usuario','activo','categoria','imagen')