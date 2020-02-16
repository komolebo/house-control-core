from django.contrib import admin
from django.urls import path, include
from rest_framework import routers
from app import views


router = routers.DefaultRouter()

router.register(r'sensors', views.SensorView, 'sensors')


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls))
]
