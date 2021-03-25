from django.contrib import admin
from app.models.models import Sensor

# Register your models here.
class SensorAdmin(admin.ModelAdmin):
    list_display = ('id', 'mac', 'name', 'status', 'state')

admin.site.register(Sensor, SensorAdmin)
