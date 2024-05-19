from rest_framework import routers
from .views import ServicioViewSet

app_name = 'api'

router = routers.DefaultRouter()

router.register('servicio',ServicioViewSet, 'servicio_api')

urlpatterns = router.urls