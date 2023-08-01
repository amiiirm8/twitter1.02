# from django.urls import path
# from . import views


# urlpatterns = [
#     path('', views.home, name="home"),
#     path('profile_list/', views.profile_list, name='profile_list'),
#     path('profile/<int:pk>', views.profile, name='profile'),
#     path('profile/followers/<int:pk>', views.followers, name='followers'),
#     path('profile/follows/<int:pk>', views.follows, name='follows'),
#     path('login/', views.login_user, name='login'),
#     path('logout', views.logout_user, name='logout'),
#     path('register/', views.register_user, name='register'),
#     path('update_user/', views.update_user, name='update_user'),
#     path('tweet_like/<int:pk>', views.tweet_like, name="tweet_like"),
#     path('tweet_show/<int:pk>', views.tweet_show, name="tweet_show"),
#     path('unfollow/<int:pk>', views.unfollow, name="unfollow"),
#     path('follow/<int:pk>', views.follow, name="follow"),
#     path('delete_tweet/<int:pk>', views.delete_tweet, name="delete_tweet"),
#     path('edit_tweet/<int:pk>', views.edit_tweet, name="edit_tweet"),
#     path('search', views.search, name='search'),

# ]
from django import views
from django.urls import path
from .views import CustomLoginView, HomeView, ProfileListView, TweetCommentView, TweetCreateView, UnfollowView, FollowView, ProfileView, FollowersView, FollowsView, LoginView, LogoutView,  EditProfileView,TweetLikeView, TweetShowView, TweetDeleteView, TweetEditView, TweetSearchView,RegisterUserView
#from .views import create_tweet


urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('profile_list/', ProfileListView.as_view(), name='profile_list'),
    path('unfollow/<int:pk>/', UnfollowView.as_view(), name='unfollow'),
    path('follow/<int:pk>/', FollowView.as_view(), name='follow'),
    path('profile/<int:pk>/', ProfileView.as_view(), name='profile'),
    path('followers/<int:pk>/', FollowersView.as_view(), name='followers'),
    path('follows/<int:pk>/', FollowsView.as_view(), name='follows'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
   # path('signup/', SignUpView.as_view(), name='signup'),
    path('edit_profile/', EditProfileView.as_view(), name='edit_profile'),

    path('like/<int:pk>/', TweetLikeView.as_view(), name='tweet_like'),
    path('tweet/<int:pk>/', TweetShowView.as_view(), name='tweet_show'),
    path('comments/<int:tweet_id>/<str:on>/', TweetCommentView.as_view(), name='comment_create'),

    #path('create_tweet/', create_tweet, name='tweet_create'),
    path('create_tweet/', TweetCreateView.as_view(), name='tweet_create'),

    path('delete/<int:pk>/', TweetDeleteView.as_view(), name='delete_tweet'),
    path('edit/<int:pk>/', TweetEditView.as_view(), name='edit_tweet'),
    path('search/', TweetSearchView.as_view(), name='tweet_search'),
    path('register/', RegisterUserView.as_view(), name='register'),

]