from django.test import TestCase
from django.contrib.auth.models import User
from .models import Tweet, UserProfile
from django.contrib.auth import get_user_model
from .models import Tweet, Comment, Media

class SoftManagerTestCase(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='testuser1', password='password')
        self.profile1 = UserProfile.objects.create(user=self.user1, username='testuser1profile')
        self.tweet1 = Tweet.objects.create(user=self.user1, body='test tweet 1')
        self.tweet2 = Tweet.objects.create(user=self.user1, body='test tweet 2')
        self.tweet3 = Tweet.objects.create(user=self.user1, body='test tweet 3', is_active=False)

    def test_soft_delete(self):
        tweets = Tweet.objects.all()
        self.assertEqual(tweets.count(), 3)
        tweets.delete()
        self.assertEqual(tweets.count(), 0)
        self.assertEqual(UserProfile.objects.filter(is_active=False).count(), 1)
        self.assertEqual(User.objects.filter(is_active=False).count(), 1)
        self.assertEqual(Tweet.objects.filter(is_active=False).count(), 3)

    def test_user_profile_creation(self):
        self.assertEqual(UserProfile.objects.count(), 1)
        self.assertEqual(self.profile.user, self.user)
        self.assertEqual(self.profile.username, 'testuserprofile')

    def test_profile_followers(self):
        follower_user = User.objects.create_user(username='follower', password='testpass')
        follower_profile = UserProfile.objects.create(user=follower_user, username='followerprofile')
        self.profile.follows.add(follower_profile)
        self.assertEqual(self.profile.user_followers().count(), 1)
        self.assertEqual(self.profile.user_followers().first().username, 'followerprofile')

    def test_profile_following(self):
        following_user = User.objects.create_user(username='following', password='testpass')
        following_profile = UserProfile.objects.create(user=following_user, username='followingprofile')
        self.profile.follows.add(following_profile)
        self.assertEqual(self.profile.user_following().count(), 1)
        self.assertEqual(self.profile.user_following().first().username, 'followingprofile')

    def test_profile_is_followed(self):
        other_user = User.objects.create_user(username='other', password='testpass')
        other_profile = UserProfile.objects.create(user=other_user, username='otherprofile')
        self.profile.follows.add(other_profile)
        self.assertTrue(self.profile.is_followed(other_profile))
        self.assertFalse(other_profile.is_followed(self.profile))

    def test_profile_follow(self):
        other_user = User.objects.create_user(username='other', password='testpass')
        other_profile = UserProfile.objects.create(user=other_user, username='otherprofile')
        self.profile.follow(other_profile)
        self.assertTrue(self.profile.is_followed(other_profile))
        self.assertFalse(other_profile.is_followed(self.profile))

    def test_profile_unfollow(self):
        other_user = User.objects.create_user(username='other', password='testpass')
        other_profile = UserProfile.objects.create(user=other_user, username='otherprofile')
        self.profile.follows.add(other_profile)
        self.profile.unfollow(other_profile)
        self.assertFalse(self.profile.is_followed(other_profile))
        self.assertFalse(other_profile.is_followed(self.profile))

    def test_profile_archive(self):
        tweet = Tweet.objects.create(user_account=self.profile, content='test tweet')
        self.profile.archive()
        self.assertFalse(self.profile.is_active)
        self.assertFalse(self.profile.user.is_active)
        self.assertFalse(tweet.is_active)

    def test_profile_restore(self):
        tweet = Tweet.objects.create(user_account=self.profile, content='test tweet')
        self.profile.archive()
        self.profile.restore()
        self.assertTrue(self.profile.is_active)
        self.assertTrue(self.profile.user.is_active)
        self.assertTrue(tweet.is_active)

class CommentTestCase(TestCase):
    def setUp(self):
        self.user1 = get_user_model().objects.create_user(username='testuser1', password='password')
        self.tweet1 = Tweet.objects.create(user=self.user1, body='test tweet 1')
        self.comment1 = Comment.objects.create(author=self.user1, tweet=self.tweet1, content='test comment 1')
        self.comment2 = Comment.objects.create(author=self.user1, tweet=self.tweet1, content='test comment 2', number_of_likes=3)

    def test_is_liked_by_user(self):
        self.assertEqual(self.comment1.is_liked_by_user(self.user1), False)
        self.comment1.likes.add(self.user1)
        self.assertEqual(self.comment1.is_liked_by_user(self.user1), True)

    def test_like_comment(self):
        self.assertEqual(self.comment1.like_comment(self.user1), True)
        self.assertEqual(self.comment1.like_comment(self.user1), False)

    def test_unlike_comment(self):
        self.comment1.likes.add(self.user1)
        self.assertEqual(self.comment1.unlike_comment(self.user1), True)
        self.assertEqual(self.comment1.unlike_comment(self.user1), False)

    def test_number_of_likes(self):
        self.assertEqual(self.comment1.number_of_likes(), 0)
        self.assertEqual(self.comment2.number_of_likes(), 3)

    def test_number_of_likes_annotate(self):
        self.assertEqual(self.comment1.number_of_likes_annotate(), 0)
        self.assertEqual(self.comment2.number_of_likes_annotate(), 3)


class MediaTestCase(TestCase):
    def setUp(self):
        self.user1 = get_user_model().objects.create_user(username='testuser1', password='password')
        self.tweet1 = Tweet.objects.create(user=self.user1, body='test tweet 1')
        self.media1 = Media.objects.create(tweet=self.tweet1, file='test.jpg')

    def test_str(self):
        self.assertEqual(str(self.media1), 'test tweet 1 - test.jpg')