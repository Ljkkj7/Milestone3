from django.shortcuts import render
from rest_framework import generics, permissions
from .models import Comment
from .serializers import CommentSerializer
from django.contrib.auth.models import User

# Create your views here.

class CommentListCreateView(generics.ListCreateAPIView):
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """
        Return comments for the target user.
        """
        target_user_id = self.request.query_params.get('target_user')
        return Comment.objects.filter(target_user_id=target_user_id).order_by('-created_at')
    

    def perform_create(self, serializer):
        """
        Save the comment with the author set to the current user.
        """
        target_user_id = self.request.data.get('target_user')
        target_user = User.objects.get(id=target_user_id)
        serializer.save(author=self.request.user, target_user=target_user)

