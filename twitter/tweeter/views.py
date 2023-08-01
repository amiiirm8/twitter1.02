
from django.db import IntegrityError
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.views import View
from django.views.generic import ListView, DetailView
from .models import AdminProfile, Comment, Profile, UserProfile
from django.contrib import messages
from .forms import CommentForm, CustomUserCreationForm, LoginForm, TweetForm, ProfilePicForm
from .models import Tweet
from django.contrib.auth import authenticate, login,logout
from django.contrib.auth.forms import UserCreationForm
from django import forms
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import CreateView, DeleteView, DetailView, UpdateView
from .forms import TweetForm
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from .forms import TweetForm
from .models import Tweet
from django.template.loader import render_to_string
from django.utils.decorators import method_decorator

from django.db.models import Q, Value
from django.db.models.functions import Coalesce
from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import UserProfile, AdminProfile
from django.db import models
from itertools import chain
from django.db.models import CharField, Value

from django.contrib.auth.views import LoginView

class CustomLoginView(LoginView):
    template_name = 'login.html'






class HomeView(LoginRequiredMixin, View):
    def get(self, request):
        tweet_form = TweetForm()
        comment_form = CommentForm()
        tweets = Tweet.objects.all().order_by("created_at")
        tweet_ids = [tweet.id for tweet in tweets]
        comments = Comment.objects.filter(tweet_id__in=tweet_ids).select_related('author', 'author__userprofile')
        comments_dict = {}
        for comment in comments:
            if comment.tweet_id not in comments_dict:
                comments_dict[comment.tweet_id] = []
            comments_dict[comment.tweet_id].append(comment)
        context = {
            'tweets': tweets,
            'tweet_form': tweet_form,
            'comment_form': comment_form,
            'comments_dict': comments_dict,
        }
        return render(request, 'home.html', context)

    def post(self, request):
        tweet_form = TweetForm(request.POST or None)
        comment_form = CommentForm(request.POST or None)
        if tweet_form.is_valid():
            tweet = tweet_form.save(commit=False)
            tweet.user = request.user
            tweet.save()
            messages.success(request, "Your tweet has been posted!")
            return redirect('home')
        if comment_form.is_valid():
            comment = comment_form.save(commit=False)
            comment.tweet_id = request.POST.get('tweet_id')
            comment.author = request.user
            comment.save()
            messages.success(request, "Your comment has been posted!")
            return redirect('home')
        tweets = Tweet.objects.all().order_by("-created_at")
        tweet_ids = [tweet.id for tweet in tweets]
        comments = Comment.objects.filter(tweet_id__in=tweet_ids).select_related('author', 'author__userprofile')
        comments_dict = {}
        for comment in comments:
            if comment.tweet_id not in comments_dict:
                comments_dict[comment.tweet_id] = []
            comments_dict[comment.tweet_id].append(comment)
        context = {
            'tweets': tweets,
            'tweet_form': tweet_form,
            'comment_form': comment_form,
            'comments_dict': comments_dict,
        }
        messages.error(request, "Invalid form.")
        return render(request, 'home.html', context)



class TweetCreateView(LoginRequiredMixin, CreateView):
    model = Tweet
    form_class = TweetForm
    template_name = 'tweet_create.html'
    success_url = reverse_lazy('home')

    def form_valid(self, form):
        form.instance.user = self.request.user
        messages.success(self.request, 'Your tweet was posted successfully.')
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'There was an error posting your tweet. Please try again.')
        return super().form_invalid(form)

    def get_success_url(self):
        return self.success_url

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        if self.request.user.is_authenticated:
            if hasattr(self.request.user, 'userprofile'):
                kwargs['userprofile'] = self.request.user.userprofile
            elif hasattr(self.request.user, 'adminprofile'):
                kwargs['adminprofile'] = self.request.user.adminprofile
        return kwargs


class ProfileListView(LoginRequiredMixin, ListView):
    template_name = "profile_list.html"
    context_object_name = "user_profiles"

    def get_queryset(self):
        user_profiles = UserProfile.objects.annotate(profile_type=Value('userprofile', output_field=CharField()))
        admin_profiles = AdminProfile.objects.annotate(profile_type=Value('adminprofile', output_field=CharField()))
        queryset = list(chain(user_profiles, admin_profiles))
        return queryset
        

class UnfollowView(LoginRequiredMixin, View):
    login_url = 'login'
    redirect_field_name = 'redirect_to'

    def get(self, request, pk):
        profile = get_object_or_404(Profile, user_id=pk)
        if request.user.is_authenticated:
            if hasattr(request.user, 'userprofile'):
                request.user.userprofile.follows.remove(profile)
                request.user.userprofile.save()
            elif hasattr(request.user, 'adminprofile'):
                request.user.adminprofile.follows.remove(profile)
                request.user.adminprofile.save()
        messages.success(request, (f"You have successfully unfollowed {profile.user.username} "))
        return redirect(request.META.get("HTTP_REFERER"))



class FollowView(LoginRequiredMixin, View):
    login_url = 'login'
    redirect_field_name = 'redirect_to'

    def get(self, request, pk):
        profile = get_object_or_404(Profile, user_id=pk)
        if request.user.is_authenticated:
            if hasattr(request.user, 'userprofile'):
                request.user.userprofile.follows.add(profile)            
                request.user.userprofile.save()
            elif hasattr(request.user, 'adminprofile'):
                request.user.adminprofile.follows.add(profile)
                request.user.adminprofile.save()
        messages.success(request, (f"You have successfully followed {profile.user.username} "))
        return redirect(request.META.get("HTTP_REFERER"))
    


class ProfileView(LoginRequiredMixin, View):
    
    def get(self, request, pk):
        # Retrieve user account
        try:
            user_profile = UserProfile.objects.get(user_id=pk)
            profile = user_profile
        except UserProfile.DoesNotExist:
            try:
                admin_profile = AdminProfile.objects.get(user_id=pk)
                profile = admin_profile
            except AdminProfile.DoesNotExist:
                return render(request, "404.html")

        tweets = Tweet.objects.filter(user_id=pk).order_by("-created_at")
        tweet = tweets.first() if tweets.exists() else None
        owner = profile.user
        account = profile

        # Determine whether current user is following profile
        current_user_profile = None
        is_following = False
        if request.user.is_authenticated:
            if hasattr(request.user, 'userprofile'):
                current_user_profile = request.user.userprofile
            elif hasattr(request.user, 'adminprofile'):
                current_user_profile = request.user.adminprofile
            if current_user_profile:
                is_following = current_user_profile.follows.filter(pk=account.pk).exists()

        return render(request, "profile.html", {"profile": profile, "tweet": tweet, "tweets": tweets, "owner": owner, "account": account, "is_following": is_following})
    

    def post(self, request, pk):
        # Retrieve user account
        try:
            user_profile = UserProfile.objects.get(user_id=pk)
            profile = user_profile
        except UserProfile.DoesNotExist:
            try:
                admin_profile = AdminProfile.objects.get(user_id=pk)
                profile = admin_profile
            except AdminProfile.DoesNotExist:
                return render(request, "404.html")

        current_user_profile = None
        action = request.POST['follow'] 
        if request.user.is_authenticated:
            if hasattr(request.user, 'userprofile'):
                current_user_profile = request.user.userprofile
            elif hasattr(request.user, 'adminprofile'):
                current_user_profile = request.user.adminprofile
            if current_user_profile:
                if action == "unfollow":
                    current_user_profile.follows.remove(profile)
                elif action == "follow":
                    current_user_profile.follows.add(profile)
                current_user_profile.save()

        tweet = Tweet.objects.filter(author_id=pk).order_by('-created_at').first()
        owner = profile.user
        account = profile
        is_following = False
        if current_user_profile:
            is_following = current_user_profile.follows.filter(pk=account.pk).exists()

        return render(request, "profile.html", {"profile": profile, "tweet": tweet, "owner": owner, "account": account, "is_following": is_following})

 
class FollowersView(LoginRequiredMixin, View):

    def get(self, request, pk):
        if request.user.id == pk:
            owner = User.objects.get(pk=pk)
            if hasattr(owner, 'userprofile'):
                profiles = owner.userprofile.followers.select_related('user__userprofile')
            elif hasattr(owner, 'adminprofile'):
                profiles = owner.adminprofile.followers.select_related('user__adminprofile')
            else:
                profiles = Profile.objects.none()
            return render(request, 'followers.html', {"profiles":profiles})
        else:
            messages.success(request, ("That's not your profile page  "))
            return redirect('home')



class FollowsView(LoginRequiredMixin, View):

    def get(self, request, pk):
        if request.user.id == pk:
            owner = User.objects.get(pk=pk)
            if hasattr(owner, 'userprofile'):
                profiles = owner.userprofile.follows.select_related('user__userprofile')
            elif hasattr(owner, 'adminprofile'):
                profiles = owner.adminprofile.follows.select_related('user__adminprofile')
            else:
                profiles = Profile.objects.none()
            return render(request, 'follows.html', {"profiles":profiles})
        else:
            messages.success(request, ("That's not your profile page  "))
            return redirect('home')
        



class LoginView(View):
    template = 'tweeter/login.html'
    form_class = LoginForm

    def get(self, request):
        form = self.form_class
        return render(request, self.template, {'form': form})

    def post(self, request):
        form = self.form_class(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            user = authenticate(request, username=cd['username'], password=cd['password'])
            if user is not None:
                login(request, user)
                messages.success(request, (f"{cd['username']}You Have Been Logged In!"))
                return redirect('home', permanent=True)
            else:
                try:
                    admin = AdminProfile.objects.get(username=cd['username'])
                    user = admin.user
                    user = authenticate(request, username=user.username, password=cd['password'])
                    if user is not None:
                        login(request, user)
                        messages.success(request, (f"{cd['username']}You Have Been Logged In!"))
                        return redirect('home', permanent=True)
                except AdminProfile.DoesNotExist:
                    pass
                messages.success(request, ("There was an error Logging. Please try again."))
                return render(request, self.template, {'form':form})

        return redirect('login')
    

class LogoutView(View):
    def get(self, request):
        logout(request)
        messages.success(request, ("You Have Been Logged Out!"))
        return redirect('login')



class EditProfileView(LoginRequiredMixin, View):
    form_class = ProfilePicForm
    template_name = 'edit_profile.html'

    def get(self, request):
        if request.user.is_superuser or request.user.is_staff:
            profile = request.user.adminprofile
        else:
            profile = request.user.userprofile

        form = self.form_class(instance=profile)
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        if request.user.is_superuser or request.user.is_staff:
            profile = request.user.adminprofile
        else:
            profile = request.user.userprofile

        form = self.form_class(request.POST or None, request.FILES or None, instance=profile)

        if form.is_valid():
            form.save()
            messages.success(request, "Changes saved successfully", 'success')
            return redirect(reverse('profile', kwargs={'username': request.user.username}))
        else:
            messages.error(request, "Error saving changes", 'danger')

        return render(request, self.template_name, {'form': form})
    

    

class TweetLikeView(LoginRequiredMixin, View):
    def post(self, request, pk):
        tweet = get_object_or_404(Tweet, id=pk)
        if tweet.likes.filter(id=request.user.id).exists():
            tweet.likes.remove(request.user)
        else:
            tweet.likes.add(request.user)
        return redirect(request.META.get("HTTP_REFERER"))


class TweetShowView(DetailView):
    model = Tweet
    template_name = "show_tweet.html"


class TweetDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Tweet
    success_url = reverse_lazy('home')
    template_name = 'delete_tweet.html'

    def test_func(self):
        tweet = self.get_object()
        return self.request.user == tweet.user


class TweetEditView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Tweet
    form_class = TweetForm
    template_name = 'edit_tweet.html'

    def test_func(self):
        tweet = self.get_object()
        return self.request.user == tweet.user

    def form_valid(self, form):
        form.instance.user = self.request.user
        messages.success(self.request, "Your tweet has been updated!")
        return super().form_valid(form)


class TweetSearchView(View):
    def post(self, request):
        search = request.POST['search']
        searched = Tweet.objects.filter(body__contains=search)
        return render(request, 'search.html', {'search': search, 'searched': searched})

    def get(self, request):
        return render(request, 'search.html', {})
    

class RegisterUserView(CreateView):
    form_class = CustomUserCreationForm
    template_name = 'register.html'
    success_url = reverse_lazy('home')

    def get(self, request):
        form = self.form_class
        return render(request, 'register.html', {'form': form})

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST, request.FILES)
        if form.is_valid():
            cd = form.cleaned_data
            try:
                account = UserProfile.create_account(
                    username=cd['username'], 
                    password=cd['password1'], 
                    first_name=cd['first_name'], 
                    last_name=cd['last_name'], 
                    profile_bio=cd['profile_bio'],
                    birthdate=cd['birthdate'], 
                    profile_image=cd['profile_image']
                )
            except IntegrityError:
                messages.error(request, 'This username is already taken', 'warning')
                user = None
            else:
                user = account.user
            if user is not None:
                login(request, user)
                messages.success(request, f"{cd['username']} registered successfully", 'success')
                return redirect('accounts:profile', cd['username'])
            else:
                messages.error(request, 'An error occurred while registering the user', 'warning')
        else:
            messages.error(request, 'Invalid form submission', 'warning')
        return render(request, self.template_name, {'form': form})


    
class TweetCommentView(LoginRequiredMixin, View):
    def post(self, request, tweet_id, on):
        tweet = get_object_or_404(Tweet, id=tweet_id)
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.tweet = tweet
            comment.author = request.user
            comment.save()
            messages.success(request, 'Comment registered successfully.')
            if on == 'tweet':
                data = {
                    'content': comment.content,
                    'name': comment.author.username,
                    'time': comment.created_at,
                    'profile_image': comment.author.profile.profile_image.url,
                    'page': reverse('home')
                }
                return JsonResponse(data)
            elif on == 'reply':
                return redirect('tweets:detail', tweet_id=tweet_id)
        else:
            messages.error(request, 'Invalid comment.')
        return redirect('tweets:detail', tweet_id=tweet_id)
    

    @login_required
    def tweet_create(request):
        if request.method == 'POST':
            form = TweetForm(request.POST, request.FILES)
            if form.is_valid():
                tweet = form.save(commit=False)
                tweet.user = request.user
                tweet.save()
                messages.success(request, 'Your tweet has been posted!')
                return redirect('home')
            else:
                messages.error(request, 'Please correct the errors below.')
        else:
            form = TweetForm()
        return render(request, 'tweets/tweet_create.html', {'form': form})
    
class CommentCreateView(LoginRequiredMixin, CreateView):
    model = Comment
    form_class = CommentForm
    template_name = 'tweets/includes/comment_form.html'
    success_url = reverse_lazy('home')

    def form_valid(self, form):
        tweet_id = self.request.POST.get('tweet_id')
        tweet = get_object_or_404(Tweet, id=tweet_id)
        comment = form.save(commit=False)
        comment.tweet = tweet
        comment.author = self.request.user
        comment.save()
        messages.success(self.request, 'Comment registered successfully.')
        data = {
            'content': comment.content,
            'name': comment.author.username,
            'time': comment.created_at,
            'profile_image': comment.author.profile.profile_image.url,
            'page': reverse('home')
        }
        return JsonResponse(data)


class TweetDetailView(DetailView):
    model = Tweet
    template_name = 'tweets/tweet_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['comment_form'] = CommentForm()
        comments = Comment.objects.filter(tweet=self.object).select_related('user__userprofile', 'user__adminprofile')
        context['comments'] = comments
        return context

    def post(self, request, *args, **kwargs):
        tweet = self.get_object()
        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            comment = comment_form.save(commit=False)
            comment.user = request.user
            comment.tweet = tweet
            comment.save()
            messages.success(request, 'Your comment was posted successfully.')
        else:
            comments = Comment.objects.filter(tweet=tweet).select_related('user__userprofile', 'user__adminprofile')
            context = {
                'tweet': tweet,
                'comments': comments,
                'comment_form': comment_form,
            }
            messages.error(request, 'There was an error posting your comment. Please try again.')
            return render(request, self.template_name, context)
        
        return redirect('tweets:tweet_detail', pk=tweet.pk)