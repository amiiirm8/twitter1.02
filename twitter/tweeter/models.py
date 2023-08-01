from audioop import reverse
from pdb import post_mortem
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db.models import Count

from django.contrib.auth import get_user_model
from django.forms import ValidationError
from django.contrib.auth import user_logged_in



class SoftQuerySet(models.QuerySet):
    def delete(self):
        for account in self:
            account.user.is_active = False
            account.user.save()
        return self.update(is_active=False)
    
class SoftManager(models.Manager):
    def get_queryset(self):
        return SoftQuerySet(self.model, self._db).filter(is_active = True)
    


class Tweet(models.Model):
    user = models.ForeignKey(User, related_name="tweets", on_delete=models.CASCADE)
    body = models.CharField(max_length=280)
    created_at = models.DateTimeField(auto_now_add=True)
    likes = models.ManyToManyField(User, related_name="tweet_likes", blank=True)
    # media = models.ImageField(null=True, blank=True, upload_to="tweet_media/")
    # hashtags = models.ManyToManyField("Hashtag", related_name="tweets", blank=True)
    comments = models.ManyToManyField("Comment", related_name="tweet_comments", blank=True)
    text = models.CharField(max_length=280, default='')

    def is_liked_by_user(self, user):
        return self.likes.filter(id=user.id).exists()

    def like_tweet(self, user):
        if not self.is_liked_by_user(user):
            self.likes.add(user)
            return True
        else:
            return False

    def unlike_tweet(self, user):
        if self.is_liked_by_user(user):
            self.likes.remove(user)
            return True
        else:
            return False

    def number_of_likes(self):
        return self.likes.count()

    def number_of_comments(self):
        return self.comments.count()

    def number_of_likes_annotate(self):
        return self.likes.annotate(num_likes=Count('id')).values_list('num_likes', flat=True).first() or 0

    def number_of_comments_annotate(self):
        return self.comments.annotate(num_comments=Count('id')).values_list('num_comments', flat=True).first() or 0

    # def clean_media(self):
    #     media = self.cleaned_data.get('media', False)
    #     if media:
    #         # Ensure that the uploaded file is an image
    #         content_type = media.content_type.split('/')[0]
    #         if content_type in ['image']:
    #             return media
    #         else:
    #             raise ValidationError("File type not supported.")
    #     else:
    #         raise ValidationError("Couldn't read uploaded file.")

    def __str__(self):
        return self.body

    
from django.contrib.auth.models import User

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    follows = models.ManyToManyField("self",
        related_name="followed_by",
        symmetrical=False,
        blank=True)
    tweets = models.ManyToManyField(Tweet, related_name="posted_by")
    
    profile_image = models.ImageField(null=True, blank=True, upload_to="images/")
    profile_bio = models.TextField(null=True, blank=True, max_length=250)
    website_link = models.CharField(null=True, blank=True, max_length=250)
    facebook_link = models.CharField(null=True, blank=True, max_length=250)
    instagram_link = models.CharField(null=True, blank=True, max_length=250)
    linkedin_link = models.CharField(null=True, blank=True, max_length=250)

    birthdate = models.DateField(("Birthdate"), default='2000-01-01')
    is_active = models.BooleanField(("Is_Active"), default=True)

    class Meta:
        abstract = True

    objects = SoftManager()
    

    def user_followers(self):
        return self.followers.all()

    def user_following(self):
        return self.following.all()

    def is_followed(self, other):
        return Profile.objects.filter(follows=self, followed_by=other).exists()

    def follow(self, other):
        if not self.is_followed(other) and self != other:
            self.follows.add(other)
            self.save()

    def unfollow(self, other):
        if self.is_followed(other):
            self.follows.remove(other)
            self.save()

    def archive(self):
        Tweet.objects.filter(user_account=self).update(is_active=False)
        self.is_active = False
        self.user.is_active = False
        self.save()
        self.user.save()

    def restore(self):
        TweetRecycle.objects.filter(user_account=self).update(is_active=True)
        self.is_active = True
        self.user.is_active = True
        self.save()
        self.user.save()

    def __str__(self):
        return self.user.username
    
    @classmethod
    def create_profile(cls, sender, instance, created, **kwargs):
        if created:
            UserProfile.objects.create(user=instance)
    


class UserProfile(Profile):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='userprofile')
    tweets = models.ManyToManyField(Tweet, related_name="user_profiles_tweets")
    username = models.CharField(max_length=30, unique=True)

    @classmethod
    def create_account(cls, username, password, profile_bio, birthdate, profile_image=None, **kwargs):
        user = User.objects.create_user(username=username, password=password, **kwargs)
        if not profile_image:
            return cls.objects.create(user=user, username=username, profile_bio=profile_bio, birthdate=birthdate)
        return cls.objects.create(user=user, username=username, profile_image=profile_image, profile_bio=profile_bio, birthdate=birthdate)


class AdminProfile(Profile):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='adminprofile')
    tweets = models.ManyToManyField(Tweet, related_name="admin_profiles_tweets")
    is_staff = models.BooleanField(default=True)
    is_superuser = models.BooleanField(default=False)



class ProfileManager(models.Manager):
    def get_profile(self, user):
        if user.is_authenticated:
            if hasattr(user, 'userprofile'):
                return user.userprofile
            elif hasattr(user, 'adminprofile'):
                return user.adminprofile
        else:
            return None



class AccountRecycle(models.Model):
    user_account = models.OneToOneField(UserProfile, on_delete=models.CASCADE)
    deleted_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    archived = models.BooleanField(default=False)


    def __str__(self):
        return f"{self.user_account.user.username} (deleted at {self.deleted_at})"



class TweetRecycle(Tweet):

    archived = models.Manager()

    class Meta:
        proxy = True
        verbose_name = ("Recycle Tweet")




# class Hashtag(models.Model):
#     name = models.CharField(max_length=50, unique=True)
#     description = models.TextField(null=True, blank=True)
#     created_at = models.DateTimeField(auto_now_add=True)
#     likes = models.ManyToManyField(User, related_name="hashtag_likes", blank=True)
#     comments = models.ManyToManyField("Comment", related_name="hashtag_comments", blank=True)

#     def is_liked_by_user(self, user):
#         return self.likes.filter(id=user.id).exists()

#     def like_hashtag(self, user):
#         if not self.is_liked_by_user(user):
#             self.likes.add(user)
#             return True
#         else:
#             return False

#     def unlike_hashtag(self, user):
#         if self.is_liked_by_user(user):
#             self.likes.remove(user)
#             return True
#         else:
#             return False

#     def number_of_likes(self):
#         return self.likes.count()

#     def number_of_comments(self):
#         return self.comments.count()

#     def number_of_likes_annotate(self):
#         return self.likes.annotate(num_likes=Count('id')).values_list('num_likes', flat=True).first() or 0

#     def number_of_comments_annotate(self):
#         return self.comments.annotate(num_comments=Count('id')).values_list('num_comments', flat=True).first() or 0

#     def __str__(self):
#         return self.name


class Comment(models.Model):
    author = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    tweet = models.ForeignKey("Tweet", on_delete=models.CASCADE, related_name="comment_set")
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    likes = models.ManyToManyField(get_user_model(), related_name='liked_comments')

    def is_liked_by_user(self, user):
        return self.likes.filter(id=user.id).exists()

    def like_comment(self, user):
        if not self.is_liked_by_user(user):
            self.likes.add(user)
            return True
        else:
            return False

    def unlike_comment(self, user):
        if self.is_liked_by_user(user):
            self.likes.remove(user)
            return True
        else:
            return False

    def number_of_likes(self):
        return self.likes.count()

    def number_of_likes_annotate(self):
        from django.db.models import Count
        return self.likes.annotate(num_likes=Count('id')).values_list('num_likes', flat=True).first() or 0

    class Meta:
        verbose_name = "Comment"
        ordering = ['created_at']
        verbose_name_plural = "Comments"

    def __str__(self):
        return self.author.username

    def get_absolute_url(self):
        return reverse("tweets:comment", args=[self.tweet.id])

class Media(models.Model):
    tweet = models.ForeignKey(Tweet, on_delete=models.CASCADE, related_name="media_files")
    file = models.FileField(upload_to='media/')
    
    def __str__(self):
        return f"{self.tweet.body} - {self.file.name}"



@receiver(post_save, sender=get_user_model())
def create_profile(sender, instance, created, **kwargs):
    if created:
        if instance.is_superuser:
            admin_profile = AdminProfile.objects.create(user=instance)
            admin_profile.save()
        else:
            user_profile = UserProfile.objects.create(user=instance)
            user_profile.save()

