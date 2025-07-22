from django.urls import path
from .views import CommentListCreateView, CommentRetrieveUpdateDestroyView

urlpatterns = [
    path('', CommentListCreateView.as_view(), name='profile-comments'),
    path('<int:pk>/', CommentRetrieveUpdateDestroyView.as_view(), name='profile-comment-detail'),
]