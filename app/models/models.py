from django.core.validators import MaxValueValidator
from django.db import models

# Create your models here.
class Sensor(models.Model):
    id = models.IntegerField(primary_key=True)
    type = models.CharField(max_length=20)
    name = models.CharField(max_length=120)
    location = models.CharField(max_length=120)
    state = models.BooleanField(default=False)
    battery = models.IntegerField(default=100)
    tamper = models.BooleanField(default=False)
    status = models.BooleanField(default=False)

    mac = models.CharField(max_length=12)
    to_update = models.BooleanField(default=False)

    def _str_(self):
        return "{} {}".format(self.name, self.mac)
