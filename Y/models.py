from django.db import models
from django.contrib.auth.models import User

# ツイートモデル
class Tweet(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.CharField(max_length=280)
    image = models.ImageField(upload_to='tweets/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    # リツイートのためのフィールド
    original_tweet = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='retweets')
    class Meta:
        unique_together = ('user', 'original_tweet')  # 同じユーザーが同じツイートをリツイートできない
    # 返信のためのフィールド
    parent_tweet = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies')

    def is_retweet(self):
        return self.original_tweet is not None

    def is_reply(self):
        return self.parent_tweet is not None

    def __str__(self):
        return f"{self.user.username}: {self.content[:50]}"
    def like_count(self):
        return self.likes.count()

# フォロー機能
class Follow(models.Model):
    follower = models.ForeignKey(User, related_name="following", on_delete=models.CASCADE)
    following = models.ForeignKey(User, related_name="followers", on_delete=models.CASCADE)

    class Meta:
        unique_together = ('follower', 'following')
# いいね機能
class Like(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    #tweet = models.ForeignKey(Tweet, on_delete=models.CASCADE)
    tweet = models.ForeignKey(Tweet, related_name="likes", on_delete=models.CASCADE)

    class Meta:
        unique_together = ('user', 'tweet')  # 同じユーザーが同じツイートにいいねできない

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(blank=True, null=True)  # 自己紹介
    profile_image = models.ImageField(upload_to='profile_pics/', blank=True, null=True)  # プロフィール画像
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username

class Notification(models.Model):
    NOTIFICATION_TYPES = (
        ('like', 'いいね'),
        ('follow', 'フォロー'),
        ('tweet', '新規ツイート'),
    )

    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sender_notifications")
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name="receiver_notifications")
    notification_type = models.CharField(max_length=10, choices=NOTIFICATION_TYPES)
    tweet = models.ForeignKey('Tweet', on_delete=models.CASCADE, null=True, blank=True)  # いいねの場合
    #message = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.sender} -> {self.receiver} ({self.notification_type})"

class DirectMessage(models.Model):
    sender = models.ForeignKey(User, related_name="sent_messages", on_delete=models.CASCADE)
    receiver = models.ForeignKey(User, related_name="received_messages", on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.sender} -> {self.receiver}: {self.content[:20]}"
