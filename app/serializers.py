from rest_framework import serializers
from app.models.models import Sensor

class SensorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sensor
        # fields = ('id', 'sn', 'name', 'status', 'description')
        fields = '__all__'
