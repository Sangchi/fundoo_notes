from django.db import models
from django.conf import settings


class Notes(models.Model):
    title = models.CharField(max_length=255, blank=False, null=False)  # corrected field name from 'titile' to 'title'
    description = models.TextField(null=True, blank=True)
    color = models.CharField(max_length=20, null=True, blank=True)
    image = models.ImageField(upload_to='note/images/', null=True, blank=True)
    is_archive = models.BooleanField(default=False, db_index=True)
    is_trash = models.BooleanField(default=False, db_index=True)
    reminder = models.DateTimeField(null=True, blank=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    def __str__(self) -> str:
        return self.title
