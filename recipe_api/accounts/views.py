from django.shortcuts import render, get_object_or_404
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status, permissions, generics
from .serializers import RegisterSerializer, LoginSerializer, ProfileSerializer, AccountDestroySerializer, FollowingSerializer, FollowersSerializer
from .models import CustomUser
from .paginations import UsersPagination, FollowingAndFollowersPagination
from rest_framework.authtoken.models import Token
from notifications.models import Notification
from django.contrib.contenttypes.models import ContentType

@api_view(['POST'])
def register(request):
    serializer = RegisterSerializer(data = request.data)
    
    try:
        """The registration logic in a try-except block to 
        catch any potential errors and provide a clear responses."""

        if serializer.is_valid():
            user = serializer.save()

            return Response({'message': f'User {user.username} has been created successfully'}, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
@api_view(['POST'])
def login(request):
    serializer = LoginSerializer(data = request.data)
    
    if serializer.is_valid():
        return Response(serializer.data, status=status.HTTP_200_OK)

    else: 
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LogoutAPIView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        try:
            # Deletes the user's auth token
            request.user.auth_token.delete()
            return Response({'message': 'You have successfully logged out'}, status=status.HTTP_200_OK)
        
        except Token.DoesNotExist:
            # Handles the case where there's no token
            return Response({'error': 'Token does not exist'}, status=status.HTTP_400_BAD_REQUEST)

    
class ProfileAPIView(generics.RetrieveUpdateAPIView):

    serializer_class = ProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user
    
    def perform_update(self, serializer):

        serializer.save()
        return Response({'message': 'Profile updated successfully'}, status=status.HTTP_200_OK)
        
class AccountDestroyAPIView(generics.RetrieveDestroyAPIView):
    serializer_class = AccountDestroySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user
    
    def destroy(self, request):  

        """ This method handles the deletion of the user(account) to add a custom deletion message"""

        instance = self.get_object()
        self.perform_destroy(instance)

        return Response({'message': 'Account deleted successfully'}, status=status.HTTP_200_OK)

from django.db.models import Count  

class FollowAPIView(generics.GenericAPIView):
    serializer_class = FollowingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        users = CustomUser.objects.annotate(num_followers=Count('followers')).order_by('-num_followers') #Retrieve users by most followers
        paginator = UsersPagination()
        paginated_users = paginator.paginate_queryset(users, request)

        usernames = [user.username for user in paginated_users]
        return paginator.get_paginated_response(usernames)

    def post(self, request, username):
        user_to_follow = get_object_or_404(CustomUser, username=username)

    # Prevent the user from following themselves
        if user_to_follow == request.user:
            return Response({'message': 'You cannot follow yourself'}, status=status.HTTP_400_BAD_REQUEST)

        # If already following, provide an option to unfollow
        if request.user.following.filter(username=user_to_follow.username).exists():
            return Response({'message': f'You already follow {user_to_follow.username}'}, status=status.HTTP_400_BAD_REQUEST)

        # Add the user to the current user's 'following' list
        request.user.following.add(user_to_follow)
        user_to_follow.followers.add(request.user)

        # Send a notification to the followed user
        content_type = ContentType.objects.get_for_model(user_to_follow)
        Notification.objects.create(
            recipient=user_to_follow,
            actor=request.user,
            verb='started following you',
            content_type=content_type,
            object_id=user_to_follow.id,
            read=False
        )

        return Response({'message': f'You are now following {user_to_follow.username}'}, status=status.HTTP_200_OK)

class FollowingAPIView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = FollowingSerializer
    pagination_class = FollowingAndFollowersPagination

    def get_queryset(self):
        user = self.request.user
        return user.following.all()
    
class FollowersAPIView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = FollowersSerializer
    pagination_class = FollowingAndFollowersPagination

    def get_queryset(self):
        user = self.request.user
        return user.followers.all()

class UnfollowAPIView(generics.GenericAPIView):
    serializer_class = FollowingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, username):
        user_to_unfollow = get_object_or_404(CustomUser, username=username)

        # Checks if the user has already been followed
        if not request.user.following.filter(username=user_to_unfollow.username).exists():
            return Response({'message': f'You are not following {user_to_unfollow.username}'}, status=status.HTTP_400_BAD_REQUEST)

        # remove the user to the current user's 'following' list
        request.user.following.remove(user_to_unfollow)
        
        return Response({'message': f'You have unfollowed {user_to_unfollow.username}'}, status=status.HTTP_200_OK)
    
class MarkNotificationAsReadView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        notification = get_object_or_404(Notification, pk=pk, recipient=request.user)

        # Check if the notification is already read
        if not notification.read:
            notification.read = True
            notification.save()
            return Response({"detail": "Notification marked as read."}, status=status.HTTP_200_OK)
        else:
            return Response({"detail": "Notification is already read."}, status=status.HTTP_400_BAD_REQUEST)

