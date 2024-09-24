from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.



class Users(AbstractUser):
    
    email=models.EmailField("email_address",unique=True)
    is_verified=models.BooleanField(default=False)

    USERNAME_FIELD='email'
    REQUIRED_FIELDS=['username']


    def __str__(self) -> str:
        return self.email


class Log(models.Model):
    
    method = models.CharField(null=False)
    url = models.URLField(null=False)
    count = models.IntegerField(default=1)

    class Meta:
        indexes = [
            models.Index(fields=['method', 'url']),
        ]

    def __str__(self):
        return f"{self.method} {self.url} - {self.count}"