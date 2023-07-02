from django.shortcuts import redirect, render
from .models import Profile, tweet
from django.contrib import messages


def home(request):
    if request.user.is_authenticated:
        tweets = tweet.objects.all().order_by("created_at")
    return render(request, 'home.html', {"tweets":tweets})

def profile_list(request):
    if request.user.is_authenticated:

        profiles = Profile.objects.exclude(user=request.user)
        return render(request, 'profile_list.html', {"profiles":profiles})
    else:
        messages.success(request, ("You must be logged in to view this page... "))
        return redirect('home')
    

def profile(request, pk):
    if request.user.is_authenticated:
        profile = Profile.objects.get(user_id=pk)
        tweets = tweet.objects.filter(user_id=pk).order_by("created_at")

        #post form logic
        if request.method == "POST":
            current_user_profile = request.user.profile
            action = request.POST['follow'] 
            if action == "unfollow":
                current_user_profile.follows.remove(profile)
            elif action == "follow":
                current_user_profile.follows.add(profile)
            current_user_profile.save()
        return render(request, "profile.html", {"profile":profile, "tweets":tweets})
    else:
        messages.success(request, ("You must be logged in to view this page... "))
        return redirect('home')
    
