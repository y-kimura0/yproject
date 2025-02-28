from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Tweet, Like, Profile, Notification, Follow
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, redirect
from django.http import JsonResponse
from .forms import ProfileUpdateForm, TweetForm, ProfileEditForm
from django.contrib.auth.models import User
from django.db import IntegrityError

# ツイート一覧

@login_required
def tweet_list(request):
    tweets = Tweet.objects.all().order_by("-created_at")
    
    # 各ツイートについて、ユーザーがリツイートしているかチェック
    for tweet in tweets:
        #tweet.is_retweeted = Tweet.objects.filter(original_tweet=tweet, user=request.user).exists()
        tweet.is_retweeted = tweet.retweets.filter(user=request.user).exists()

    return render(request, 'Y/tweet_list.html', {'tweets': tweets})
#@login_required
#def tweet_list(request):
    #tweets = Tweet.objects.all().order_by('-created_at')
    #return render(request, 'Y/tweet_list.html', {'tweets': tweets})

# ツイート投稿
@login_required
def tweet_create(request):
    if request.method == "POST":
        form = TweetForm(request.POST, request.FILES)
        if form.is_valid():
            tweet = form.save(commit=False)
            tweet.user = request.user
            tweet.save()
            return redirect('tweet_list')
    else:
        form = TweetForm()
    return render(request, 'Y/tweet_create.html', {'form': form})
    #if request.method == "POST":
        #content = request.POST['content']
        #Tweet.objects.create(user=request.user, content=content)
        #return redirect('tweet_list')
    #return render(request, 'Y/tweet_create.html')

# ツイート削除
@login_required
def tweet_delete(request, tweet_id):
    tweet = Tweet.objects.get(id=tweet_id)
    if tweet.user == request.user:
        tweet.delete()
    # プロフィールページから削除された場合、プロフィールページに戻る
    if 'profile' in request.META.get('HTTP_REFERER', ''):
        return redirect('profile', username=request.user.username)
    return redirect('tweet_list')

# ユーザー登録
def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('tweet_list')
    else:
        form = UserCreationForm()
    return render(request, 'Y/signup.html', {'form': form})

# ログイン
def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('tweet_list')
    return render(request, 'Y/login.html')

# ログアウト
def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def like_tweet(request, tweet_id):
    tweet = Tweet.objects.get(id=tweet_id)
    like, created = Like.objects.get_or_create(user=request.user, tweet=tweet)

    if not created:
        like.delete()
        liked = False
    else:
        liked = True
        if request.user != tweet.user:
            Notification.objects.create(
                sender=request.user,
                receiver=tweet.user,
                notification_type='like',
                tweet=tweet
            )

    return JsonResponse({"liked": liked, "like_count": tweet.like_count()})

def profile_view(request, username):
    user = get_object_or_404(User, username=username)
    profile, created = Profile.objects.get_or_create(user=user)
    tweets = Tweet.objects.filter(user=user).order_by('-created_at')
    is_following = Follow.objects.filter(follower=request.user, following=user).exists() if request.user.is_authenticated else False
    return render(request, 'Y/profile.html', {'profile': profile, 'tweets': tweets,  'is_following': is_following})

@login_required
def profile_edit(request):
    profile, created = Profile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        #form = ProfileUpdateForm(request.POST, request.FILES, instance=profile)
        form = ProfileEditForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('profile', username=request.user.username)
    else:
        #form = ProfileUpdateForm(instance=profile)
        form = ProfileEditForm(instance=profile)
    return render(request, 'Y/profile_edit.html', {'form': form})

@login_required
def follow_user(request, username):
    user_to_follow = get_object_or_404(User, username=username)
    follow, created = Follow.objects.get_or_create(follower=request.user, following=user_to_follow)

    if not created:
        follow.delete()
        followed = False
    else:
        followed = True
        if request.user != user_to_follow:
            Notification.objects.create(
                sender=request.user,
                receiver=user_to_follow,
                notification_type='follow'
            )

    return JsonResponse({"followed": followed})

@login_required
def notification_list(request):
    notifications = Notification.objects.filter(receiver=request.user, is_read=False).order_by('-created_at')
    for notification in notifications:
        notification.is_read = True
        notification.save()
    return render(request, 'Y/notifications.html', {'notifications': notifications})

@login_required
#def retweet(request, tweet_id):
    #original_tweet = get_object_or_404(Tweet, id=tweet_id)

    # すでにリツイートしているか確認
    #retweet = Tweet.objects.filter(user=request.user, original_tweet=original_tweet).first()

    #if retweet:
        #retweet.delete()  # すでにリツイート済みなら削除
    #else:
        #Tweet.objects.create(user=request.user, original_tweet=original_tweet)  # まだリツイートしていなければ作成

    #return redirect('tweet_list')
def retweet(request, tweet_id):
    original_tweet = get_object_or_404(Tweet, id=tweet_id)
    #Tweet.objects.create(user=request.user, original_tweet=original_tweet)
    retweet = Tweet.objects.create(
        user=request.user,
        content=original_tweet.content,  # 元ツイートの内容をコピー
        #image=original_tweet.image,      # 元ツイートの画像をコピー
        original_tweet=original_tweet,   # リツイート元のツイートを指定
        #is_retweet=True                  # リツイートであることを明示
    )
    return redirect('tweet_list')

@login_required
def reply(request, tweet_id):
    if request.method == "POST":
        content = request.POST.get("content")
        original_tweet = Tweet.objects.get(id=tweet_id)
        if content:
            Tweet.objects.create(user=request.user, content=content, original_tweet=original_tweet)
    return redirect("tweet_detail", tweet_id=tweet_id)
#def reply(request, tweet_id):
#    parent_tweet = get_object_or_404(Tweet, id=tweet_id)
#    if request.method == "POST":
#        content = request.POST.get("content")
#        Tweet.objects.create(user=request.user, content=content, parent_tweet=parent_tweet)
#    return redirect('tweet_list')

def tweet_detail(request, tweet_id):
    tweet = get_object_or_404(Tweet, id=tweet_id)
    replies = Tweet.objects.filter(original_tweet=tweet).order_by("created_at")  # 返信ツイートの取得
    return render(request, 'Y/tweet_detail.html', {'tweet': tweet, 'replies': replies})

def profile(request, user_id):
    user = get_object_or_404(User, id=user_id)
    tweets = Tweet.objects.filter(user=user)
    return render(request, 'Y/profile.html', {'user': user, 'tweets': tweets})