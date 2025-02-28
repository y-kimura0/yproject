from django.urls import path
from . import views
from .api_views import TweetListView, like_tweet_api, follow_user_api, NotificationListView
from .api_views import LoginAPI, LogoutAPI
from rest_framework.authtoken.views import obtain_auth_token
from .views import retweet, reply, tweet_list, tweet_detail, profile, follow_user

urlpatterns = [
    path('', views.tweet_list, name='tweet_list'),
    path('create/', views.tweet_create, name='tweet_create'),
    path('delete/<int:tweet_id>/', views.tweet_delete, name='tweet_delete'),
    path('signup/', views.signup, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('like/<int:tweet_id>/', views.like_tweet, name='like_tweet'),
    path('retweet/<int:tweet_id>/', retweet, name='retweet'),
    path('reply/<int:tweet_id>/', reply, name='reply'),
    path('profile/edit/', views.profile_edit, name='profile_edit'),
    path('profile/<str:username>/', views.profile_view, name='profile'),
    path('tweet/new/', views.tweet_create, name='tweet_create'),
    path('follow/<str:username>/', follow_user, name='follow_user'),
    path('notifications/', views.notification_list, name='notifications'),
    path('api/tweets/', TweetListView.as_view(), name='api_tweet_list'),
    path('api/tweet/<int:tweet_id>/like/', like_tweet_api, name='api_like_tweet'),
    path('api/user/<str:username>/follow/', follow_user_api, name='api_follow_user'),
    path('api/notifications/', NotificationListView.as_view(), name='api_notifications'),
    path('api/auth/login/', LoginAPI.as_view(), name='api_login'),
    path('api/auth/logout/', LogoutAPI.as_view(), name='api_logout'),
    path('api/follow/<str:username>/', follow_user_api, name='follow_user_api'),
    path('tweet/<int:tweet_id>/', tweet_detail, name='tweet_detail'),
    path('profile/<int:user_id>/', profile, name='profile'),
]
