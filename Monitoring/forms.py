from django import forms
from django.contrib.auth import authenticate, update_session_auth_hash
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

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

    def clean_username(self):
        new_username = self.cleaned_data['username']
        existing_user = User.objects.filter(username=new_username)
        if existing_user:
            self.add_error('username', "This username is already in use. Please choose a different one.")
        return new_username

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        password_check = cleaned_data.get("password_check")
        if password != password_check:
            self.add_error('password', "Passwords do not match. Please enter matching passwords.")
        return cleaned_data

    def save(self, **kwargs):
        self.cleaned_data.pop('password_check')
        user = models.User.objects.create_user(**self.cleaned_data)
        profile = models.Profile.objects.create(user=user)
        return user


class CreateTask(forms.ModelForm):
    pages_number = forms.IntegerField()

    class Meta:
        model = models.Task
        fields = ['title', 'description', 'pages_number']

    def __init__(self, *args, author=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.author = author

    def clean_pages_number(self):
        pages_number = self.cleaned_data['pages_number']
        if pages_number <= 0:
            self.add_error('pages_number', "The page number is a positive number.")
        return pages_number

    def save(self, commit=True):
        task = super().save(commit=False)
        task.author = self.author
        if commit:
            task.save()
            for page_number in range(1, self.cleaned_data['pages_number'] + 1):
                task.pages.create(number=page_number)
        return task


class CreatePage(forms.ModelForm):
    text = forms.CharField(widget=forms.Textarea)
    correct_page = forms.IntegerField(required=False)
    wrong_page = forms.IntegerField(required=False)

    class Meta:
        model = models.Page
        fields = ['text', 'correct_page', 'wrong_page']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def clean_correct_page(self):
        correct_page = self.cleaned_data['correct_page']
        if correct_page is not None and correct_page <= 0:
            self.add_error('correct_page', 'Please, enter a positive number.')
        return correct_page

    def clean_wrong_page(self):
        wrong_page = self.cleaned_data['wrong_page']
        if wrong_page is not None and wrong_page <= 0:
            self.add_error('wrong_page', 'Please, enter a positive number')
        return wrong_page

    def save(self, task, number, commit=True):
        page, created = models.Page.objects.get_or_create(task=task, number=number)
        page.text = self.cleaned_data['text']
        if not self.cleaned_data['correct_page']:
            page.correct_page = number + 1
        else:
            page.correct_page = self.cleaned_data['correct_page']
        page.wrong_page = self.cleaned_data['wrong_page']
        if commit:
            page.save()
        return page


class SettingsForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, required=False)
    password_check = forms.CharField(widget=forms.PasswordInput, required=False)
    username = forms.CharField(min_length=3, required=False)
    last_name = forms.CharField(min_length=2, required=False)
    first_name = forms.CharField(min_length=2, required=False)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'last_name', 'first_name']

    def clean_username(self):
        new_username = self.cleaned_data['username']
        existing_user = User.objects.filter(username=new_username).exclude(pk=self.instance.pk).first()
        if existing_user:
            raise ValidationError("This username is already in use. Please choose a different one.")
        return new_username

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        password_check = cleaned_data.get("password_check")

        if password and password_check and password != password_check:
            raise forms.ValidationError("Passwords do not match. Please enter matching passwords.")

        return cleaned_data

    def save(self, user, request=None, **kwargs):
        for field in self.Meta.fields:
            field_value = self.cleaned_data.get(field)
            if field_value:
                if field == 'password':
                    user.set_password(field_value)
                else:
                    setattr(user, field, field_value)
        user.save()
        if request:
            update_session_auth_hash(request, user)
        return user

class ProfileSettingsForm(forms.ModelForm):
    avatar = forms.ImageField(required=False)

    class Meta:
        model = models.Profile
        fields = ['avatar']

    def save(self, profile, **kwargs):
        avatar = self.cleaned_data.get('avatar')
        print(avatar)
        print("aboba")
        if avatar:
            profile.avatar = avatar
            profile.save()
            return profile
