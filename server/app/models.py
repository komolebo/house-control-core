from django.db import models

# Create your models here.
class Sensor(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=120)
    status = models.BooleanField(default=True)
    description = models.CharField(max_length=1000)
    sn = models.CharField(max_length=18)

    def _str_(self):
        self.name + " " + self.sn
