from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Comment(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='written_comments')
    target_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='profile_comments')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
