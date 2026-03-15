from django.db import models
from django.db import models
from django.contrib.auth.models import User
# Create your models here.

class UploadedAudio(models.Model):
    audio = models.FileField(upload_to='uploads/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

from django.db import models
from django.contrib.auth.models import User

class Profile(models.Model):
    USER_ROLES = (
        ('admin', 'Администратор'),
        ('user', 'Пользователь'),
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=10, choices=USER_ROLES, default='user')
    first_name = models.CharField(max_length=100, verbose_name='Имя')
    last_name = models.CharField(max_length=100, verbose_name='Фамилия')

    def __str__(self):
        return f"{self.user.username} - {self.role}"