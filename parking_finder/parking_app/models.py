# Create your models here.
from django.contrib.auth.models import AbstractUser
from django.contrib.gis.db import models as gis_models
from django.db import models


class CustomUser(AbstractUser):
    phone = models.CharField(max_length=20, blank=True)


class Parking(gis_models.Model):
    id = gis_models.IntegerField(primary_key=True)
    tag = gis_models.CharField(max_length=255)
    geometry = gis_models.GeometryField()
    reserved = models.BooleanField(default=False)
    user = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name="parking_spots", null=True
    )
