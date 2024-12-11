# Create your models here.
from django.db import models
from django.conf import settings
from django.utils.timezone import now

# Create your models here.
class Education(models.Model):
    degree     = models.TextField(default='')
    university = models.TextField(default='')
    startDate = models.DateTimeField(default=now, blank=True)
    endDate   = models.DateTimeField(default=now, blank=True)
    posted_by  = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.CASCADE)
