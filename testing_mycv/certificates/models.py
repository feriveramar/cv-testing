# Create your models here.
from django.db import models
from django.conf import settings
from django.utils.timezone import now

# Create your models here.
class Certificates(models.Model):
    title     = models.TextField(default='')
    institution = models.TextField(default='')
    year = models.IntegerField(default=1, blank=True)
    posted_by  = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.CASCADE)
