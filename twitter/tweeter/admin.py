from typing import Any
from django.contrib import admin
from django.contrib.auth.models import Group, User
from django.http import HttpRequest
from .models import AccountRecycle, Profile, TweetRecycle
from .models import Tweet
from django.db.models.query import QuerySet
from django.contrib import admin
from .models import UserProfile, Tweet
from django.utils.html import format_html




# Unregister Groups
# admin.site.unregister(Group)

# #Mix profile info user info
# class ProfileInLine(admin.StackedInline):
#     model = Profile


# # Extend User model
# class UserAdmin(admin.ModelAdmin):
#     model = User
#     #just display username fields on admin page
#     fields = ["username"]
#     inlines = [ProfileInLine]

# # Unregister initial User
# admin.site.unregister(User)
# # Register User and Profile
# admin.site.register(User, UserAdmin)
# admin.site.register(Tweet)

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['username', 'email', 'bio']

    def username(self, obj):
        return obj.username

    def email(self, obj):
        return obj.email

    def bio(self, obj):
        return obj.bio_text

@admin.register(Tweet)
class TweetAdmin(admin.ModelAdmin):
    

    list_display = ('id', 'tweet_text', 'user')
    list_filter = ('created_at', 'user')
    search_fields = ('text', 'user__username')

    def tweet_text(self, obj):
        return format_html('<span title="{}">{}</span>', obj.text, obj.text[:50] + '...' if len(obj.text) > 50 else obj.text)
    tweet_text.short_description = 'Text'
    

    

    def save_model(self, request, obj, form, change):
        obj.user = request.user
        obj.save()

@admin.register(AccountRecycle)
class AccountRecycleAdmin(admin.ModelAdmin):
    
    def get_queryset(self, request):
        return AccountRecycle.objects.filter(is_active=False, archived=True)

    list_display = ['field1', 'field2', 'bio']

    def field1(self, obj):
        return obj.some_attribute

    def field2(self, obj):
        return obj.some_other_attribute

    def bio(self, obj):
        return obj.bio

    @admin.action(description='Restore Archived Accounts')
    def restore(self, request, queryset):
        for account in queryset:
            account.user.is_active = True
            account.user.save()
            TweetRecycle.archived.filter(user_account=account).update(is_active=True)
        queryset.update(is_active=True)