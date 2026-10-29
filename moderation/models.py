from django.db import models
from django.conf import settings

# Create your models here.
class SuspiciousRequest(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                                 on_delete=models.CASCADE,
                                )
    arguments = models.JSONField(default=list)