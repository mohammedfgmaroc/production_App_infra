from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.contrib.auth.models import Permission
# Create your models here.

class GMTPlus1DateTimeField(models.DateTimeField):
    def pre_save(self, model_instance, add):
        value = timezone.now() + timezone.timedelta(hours=1)
        setattr(model_instance, self.attname, value)
        return value
    
class UploadedFile(models.Model):
    class ValidationStatus(models.TextChoices):
        PENDING = 'Pending', 'Pending'
        APPROVED = 'Approved', 'Approved'
        REJECTED = 'Rejected', 'Rejected'

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    filename = models.CharField(max_length=255)
    uploaded_at = GMTPlus1DateTimeField()
    validation_status = models.CharField(
        max_length=20,
        choices=ValidationStatus.choices,
        default=ValidationStatus.PENDING,
    )

    def __str__(self):
        return self.filename
    



