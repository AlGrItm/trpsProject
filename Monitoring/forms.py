from django import forms
from django.contrib.auth import authenticate

from Monitoring import models


class LoginForm(forms.Form):
    username = forms.CharField(min_length=3)
    password = forms.CharField(min_length=3, widget=forms.PasswordInput)


class RegisterForm(forms.Form):
    password = forms.CharField(min_length=3, widget=forms.PasswordInput)
    password_check = forms.CharField(min_length=3, widget=forms.PasswordInput)
    username = forms.CharField(min_length=3)
    last_name = forms.CharField(min_length=2, required=False)
    first_name = forms.CharField(min_length=2, required=False)

    def save(self, **kwargs):
        self.cleaned_data.pop('password_check')
        user = models.User.objects.create_user(**self.cleaned_data)
        profile = models.Profile.objects.create(user=user)
        return user


