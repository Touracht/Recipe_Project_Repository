from django.urls import path
from .views import register, login, LogoutAPIView, ProfileAPIView, AccountDestroyAPIView, FollowAPIView, UnfollowAPIView, FollowingAPIView, FollowersAPIView, MarkNotificationAsReadView

urlpatterns = [
    path('register/', register, name='register'),
    path('login/', login, name='login'),
    path('profile/', ProfileAPIView.as_view(), name='profile'),
    path('delete_account/', AccountDestroyAPIView.as_view(), name='detete_account'),
    path('follow/', FollowAPIView.as_view(), name='follow_users'),
    path('follow/<str:username>/', FollowAPIView.as_view(), name='follow_user'),
    path('unfollow/<str:username>/', UnfollowAPIView.as_view(), name='unfollow_user'),
    path('following/', FollowingAPIView.as_view(), name='following'),
    path('followers/', FollowersAPIView.as_view(), name='followers'),
    path('logout/', LogoutAPIView.as_view(), name='logout'),
    path('notifications/<int:pk>/read/', MarkNotificationAsReadView.as_view(), name='mark_notification_as_read'),
]
