from django.db import models
from django.conf import settings

# Create your models here.


class Label(models.Model):
    
    name = models.CharField(max_length=255, null=False)
    color = models.CharField(max_length=50, null=True, blank=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

    