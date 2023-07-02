from django.contrib import admin
from django.contrib.auth.models import Group, User
from .models import Profile

# Unregister Groups
admin.site.unregister(Group)

#Mix profile info user info
class ProfileInLine(admin.StackedInline):
    model = Profile


# Extend User model
class UserAdmin(admin.ModelAdmin):
    model = User
    #just display username fields on admin page
    fields = ["username"]
    inlines = [ProfileInLine]

# Unregister initial User
admin.site.unregister(User)
# Register User and Profile
admin.site.register(User, UserAdmin)