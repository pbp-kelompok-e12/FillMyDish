from django.db import models
from django.contrib.auth.models import User

# models.py -> mendefinisikan model Profile dan Connection untuk menyimpan informasi profil pengguna 
#              dan koneksi media sosial mereka

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    username = models.CharField(max_length=150, blank=True)
    full_name = models.CharField(max_length=255, blank=True)
    email = models.EmailField(blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    bio = models.TextField(blank=True)
    profile_image = models.ImageField(upload_to="profile_images/", blank=True)

    def __str__(self):
        return f"{self.user.username}'s profile"


class Connection(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="connections")
    platform = models.CharField(max_length=50)
    url = models.URLField()

    def __str__(self):
        return f"{self.platform}: {self.url}"
