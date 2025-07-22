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


class CommentRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        """
        Override to ensure the comment belongs to the current user.
        """
        obj = super().get_object()
        if obj.author != self.request.user:
            raise permissions.PermissionDenied("You do not have permission to edit this comment.")
        return obj
    
    def perform_update(self, serializer):
        """
        Update the comment with the current user as the author.
        """
        serializer.save(author=self.request.user)

    def perform_destroy(self, instance):
        """
        Delete the comment if it belongs to the current user.
        """
        if instance.author == self.request.user:
            instance.delete()
        else:
            raise permissions.PermissionDenied("You do not have permission to delete this comment.")






