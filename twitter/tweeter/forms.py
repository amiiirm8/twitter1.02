from typing import Any
from django import forms
from .models import Comment, Tweet, Profile 
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.forms.widgets import ClearableFileInput, CheckboxSelectMultiple, MultipleHiddenInput, SelectMultiple


class ProfilePicForm(forms.ModelForm):
    profile_image = forms.ImageField(label="Profile Picture", required=False)
    profile_bio = forms.CharField(label="Profile Bio", widget=forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Profile Bio'}), required=False)
    website_link = forms.CharField(label="", widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'website Link'}), required=False)
    facebook_link = forms.CharField(label="", widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'facebook Link'}), required=False)
    instagram_link = forms.CharField(label="", widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'instagram Link'}), required=False)
    linkedin_link = forms.CharField(label="Linkedin Link", widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'linkedin Link'}), required=False)
    username = forms.CharField(max_length=30, required=False)
    first_name = forms.CharField(max_length=30, required=False)
    last_name = forms.CharField(max_length=30, required=False)
    email = forms.EmailField(required=False)


    class Meta:
        model = Profile
        fields = ('profile_image', 'profile_bio', 'website_link', 'facebook_link', 'instagram_link', 'linkedin_link', 'username', 'first_name', 'last_name', 'email')



class TweetForm(forms.ModelForm):
    body = forms.CharField(
        required=True,
        widget=forms.widgets.Textarea(
            attrs={
                "placeholder": "Enter Your Tweet! ",
                "class": "form-control",
            }
        ),
        label="",
    )

    def __init__(self, *args, **kwargs):
        user_profile = kwargs.pop('userprofile', None)
        admin_profile = kwargs.pop('adminprofile', None)
        super().__init__(*args, **kwargs)
        if user_profile:
            self.fields['body'].widget.attrs.update({'placeholder': 'What\'s happening?'})
        elif admin_profile:
            self.fields['body'].widget.attrs.update({'placeholder': 'Post an announcement'})

    class Meta:
        model = Tweet
        fields = ('body',)
        widgets = {
            'body': forms.Textarea(attrs={'rows': 3}),
        }




class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']




class CustomUserCreationForm(UserCreationForm):
    username= forms.CharField(widget=forms.TextInput(attrs={'class':'form-control form-control-lg', 'placeholder':"Enter Username" }), required=True)
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class':'form-control form-control-lg', 'placeholder':"Enter a valid email" }), required=True)
    first_name= forms.CharField(widget=forms.TextInput(attrs={'class':'form-control form-control-lg', 'placeholder':"Enter your first name" }), required=True)
    last_name= forms.CharField(widget=forms.TextInput(attrs={'class':'form-control form-control-lg', 'placeholder':"Enter your last name" }), required=True)
    profile_bio= forms.CharField(max_length=300 ,widget=forms.Textarea(attrs={'class':'form-control form-control-lg', 'placeholder':"Write a Bio" }), required=True)
    birthdate= forms.DateField(initial="2023-07-21", widget=forms.SelectDateWidget(years=[x for x in range(1940,2024)]), required=False)
    profile_image = forms.ImageField(required=False, widget=forms.FileInput())

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super(CustomUserCreationForm, self).__init__(*args, **kwargs)

        self.fields['username'].widget.attrs['class'] = 'form-control'
        self.fields['username'].widget.attrs['placeholder'] = 'User Name'
        self.fields['username'].label = ''
        self.fields['username'].help_text = '<span class="form-text text-muted"><small>Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.</small></span>'

        self.fields['password1'].widget.attrs['class'] = 'form-control'
        self.fields['password1'].widget.attrs['placeholder'] = 'Password'
        self.fields['password1'].label = ''
        self.fields['password1'].help_text = '<ul class="form-text text-muted small"><li>Your password can\'t be too similar to your other personal information.</li><li>Your password must contain at least 8 characters.</li><li>Your password can\'t be a commonly used password.</li><li>Your password can\'t be entirely numeric.</li></ul>'

        self.fields['password2'].widget.attrs['class'] = 'form-control'
        self.fields['password2'].widget.attrs['placeholder'] = 'Confirm Password'
        self.fields['password2'].label = ''
        self.fields['password2'].help_text = '<span class="form-text text-muted"><small>Enter the same password as before, for verification.</small></span>'

class LoginForm(forms.Form):
    
    username = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control form-control-lg', 'placeholder':"Enter Username" }), required=True)
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class':'form-control form-control-lg', 'placeholder':"Enter Password"}))
