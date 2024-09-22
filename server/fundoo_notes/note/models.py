from django.db import models
from django.conf import settings
from label.models import Label


class Notes(models.Model):
    title = models.CharField(max_length=255, blank=False, null=False)  # corrected field name from 'titile' to 'title'
    description = models.TextField(null=True, blank=True)
    color = models.CharField(max_length=20, null=True, blank=True)
    image = models.ImageField(upload_to='note/images/', null=True, blank=True)
    is_archive = models.BooleanField(default=False, db_index=True)
    is_trash = models.BooleanField(default=False, db_index=True)
    reminder = models.DateTimeField(null=True, blank=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    collaborators = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        through='Collaborator',
        related_name='collaborated_notes'
    )

    labels = models.ManyToManyField(Label, related_name='notes', blank=True)

    

    def __str__(self):
        return self.title
    

class Collaborator(models.Model):
    READ_ONLY = 'read_only'
    READ_WRITE = 'read_write'

    ACCESS_TYPE_CHOICES = [
        (READ_ONLY, 'Read Only'),
        (READ_WRITE, 'Read Write'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    note = models.ForeignKey(Notes, on_delete=models.CASCADE)
    access_type = models.CharField(max_length=20, choices=ACCESS_TYPE_CHOICES)

    def __str__(self):
        return f"{self.user.email} - {self.note.title} ({self.access_type})"

   