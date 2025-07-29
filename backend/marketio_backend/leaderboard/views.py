from django.shortcuts import render
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from custom_auth.models import UserProfile
from custom_auth.serializers import UserProfileSerializer


# Create your views here.
class LeaderboardView(generics.ListAPIView):
    """
    A view to display the leaderboard of users 
    based on their experience points.
    """
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Return the top 10 users ordered by experience points.
        """
        return UserProfile.objects.order_by('-experience')[:10]    