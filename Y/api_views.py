from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from django.contrib.auth.models import User
from .models import Tweet, Notification, Follow
from .serializers import TweetSerializer, NotificationSerializer, UserSerializer
from rest_framework.authtoken.models import Token
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from rest_framework.authtoken.views import ObtainAuthToken
from django.contrib.auth import authenticate

# ツイート一覧
class TweetListView(generics.ListCreateAPIView):
    queryset = Tweet.objects.all().order_by('-created_at')
    serializer_class = TweetSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

# いいね機能
@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def like_tweet_api(request, tweet_id):
    tweet = Tweet.objects.get(id=tweet_id)
    like, created = tweet.like_set.get_or_create(user=request.user)
    
    if not created:
        like.delete()
    
    return Response({'message': 'Like toggled', 'like_count': tweet.like_set.count()})

# フォロー機能
@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def follow_user_api(request, username):
    user_to_follow = User.objects.get(username=username)
    follow, created = Follow.objects.get_or_create(follower=request.user, following=user_to_follow)
    
    if not created:
        follow.delete()
    
    return Response({'message': 'Follow toggled'})

# 通知一覧
class NotificationListView(generics.ListAPIView):
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Notification.objects.filter(receiver=self.request.user, is_read=False).order_by('-created_at')

class LoginAPI(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        return Response({'token': token.key})

class LogoutAPI(APIView):
    def post(self, request):
        request.auth.delete()
        return Response({'message': 'Logged out'})