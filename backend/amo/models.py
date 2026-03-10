from django.db import models

class Airport(models.Model):
    iata = models.CharField(max_length=3, unique=True)
    city = models.CharField(max_length=256)
    state = models.CharField(max_length=2)
    lat = models.DecimalField(max_digits=12, decimal_places=10)
    lon = models.DecimalField(max_digits=12, decimal_places=10)
