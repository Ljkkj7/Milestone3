from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from custom_auth.models import UserProfile
from custom_auth.serializers import UserProfileSerializer
from rest_framework.response import Response


# Create your views here.
class LeaderboardView(APIView):
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

    def get(self, request):
        """
        Handle GET request to retrieve the leaderboard.
        """
        queryset = self.get_queryset()
        serializer = self.serializer_class(queryset, many=True)
        return Response(serializer.data)    