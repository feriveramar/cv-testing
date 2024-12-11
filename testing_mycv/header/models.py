from django.db import models
from django.conf import settings

# Create your models here.
class Header(models.Model):
    url = models.URLField(default='')
    title     = models.TextField(default='')
    description     = models.TextField(default='')
    phone = models.TextField(default='')
    address = models.TextField(default='')
    email  = models.TextField(default='')
    socialmedia = models.TextField(default='')
    posted_by  = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.CASCADE)
