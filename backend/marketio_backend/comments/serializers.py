from rest_framework import serializers
from .models import Comment
from django.contrib.auth.models import User

class CommentSerializer(serializers.ModelSerializer):
    author_username = serializers.CharField(source='author.username', read_only=True)

    class Meta:
        model = Comment
        fields = ['id', 'author_username', 'content', 'created_at', 'updated_at', 'author_id']

