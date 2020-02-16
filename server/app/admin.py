from django.contrib import admin
from .models import Sensor

# Register your models here.
class SensorAdmin(admin.ModelAdmin):
    list_display = ('id', 'sn', 'name', 'status', 'description')

admin.site.register(Sensor, SensorAdmin)
