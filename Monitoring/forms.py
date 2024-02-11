from django import forms
from django.contrib import messages
from django.contrib.auth import authenticate, update_session_auth_hash
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils import timezone

from Monitoring import models


class LoginForm(forms.Form):
    username = forms.CharField(min_length=3, label='Логин')
    password = forms.CharField(min_length=3, widget=forms.PasswordInput, label='Пароль')

    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get('username')
        password = cleaned_data.get('password')

        user = authenticate(username=username, password=password)

        if user is None:
            raise forms.ValidationError("Неправильный логин или пароль")
        return cleaned_data


class RegisterForm(forms.Form):
    password = forms.CharField(min_length=3, widget=forms.PasswordInput, label='Пароль')
    password_check = forms.CharField(min_length=3, widget=forms.PasswordInput, label='Повторите пароль')
    username = forms.CharField(min_length=3, label='Никнейм')
    last_name = forms.CharField(min_length=2, required=False, label='Фамилия')
    first_name = forms.CharField(min_length=2, required=False, label='Имя')

    def clean_username(self):
        new_username = self.cleaned_data['username']
        existing_user = User.objects.filter(username=new_username)

        if existing_user:
            self.add_error('username', "Пользователь с таким никнеймом уже существует. Выберите другой ник")
        return new_username

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        password_check = cleaned_data.get("password_check")

        if password != password_check:
            self.add_error('password', "Пароли не совпадают")
        return cleaned_data

    def save(self, **kwargs):
        self.cleaned_data.pop('password_check')
        user = models.User.objects.create_user(**self.cleaned_data)
        profile = models.Profile.objects.create(user=user)
        return user


class CreateTask(forms.ModelForm):
    pages_number = forms.IntegerField()
    deadline = forms.DateField(widget=forms.SelectDateWidget)

    class Meta:
        model = models.Task
        fields = ['title', 'description', 'pages_number', 'deadline']

    def __init__(self, *args, author=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.author = author

    def clean_pages_number(self):
        pages_number = self.cleaned_data['pages_number']

        if pages_number <= 0:
            self.add_error('pages_number', "Количество страниц должно быть положительным числом")
        return pages_number

    def clean(self):
        cleaned_data = super().clean()
        title = cleaned_data.get('title')
        deadline = cleaned_data.get('deadline')

        if models.Task.objects.filter(title=title).exclude(id=self.instance.id).exists():
            self.add_error('title', "Задание с таким названием уже существует")

        if deadline and deadline < timezone.now().date():
            self.add_error('deadline', "Дедлайн не может быть в прошедшем времени")
        return cleaned_data

    def save(self, commit=True):
        task = super().save(commit=False)
        task.author = self.author

        if commit:
            task.save()
            for page_number in range(1, self.cleaned_data['pages_number'] + 1):
                task.pages.create(number=page_number)
        return task


class EditTaskForm(forms.ModelForm):
    class Meta:
        model = models.Task

        fields = ['title', 'description', 'deadline']

        labels = {
            'title': 'Название',
            'description': 'Описание',
            'deadline': 'Дедлайн',
        }

        widgets = {
            'deadline': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super(EditTaskForm, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs.update({'class': 'form-control'})

    def clean_deadline(self):
        deadline = self.cleaned_data['deadline']
        if deadline and deadline <= timezone.now().date():
            raise ValidationError('Дедлайн не может быть в прошлом')
        return deadline

    def clean_title(self):
        title = self.cleaned_data['title']
        existing_titles = models.Task.objects.exclude(id=self.instance.id).values_list('title', flat=True)
        if title in existing_titles:
            raise ValidationError('Задание с таким названием уже существует')
        return title


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
            self.add_error('correct_page', 'Пожалуйста, введите положительное число')
        return correct_page

    def clean_wrong_page(self):
        wrong_page = self.cleaned_data['wrong_page']
        if wrong_page is not None and wrong_page <= 0:
            self.add_error('wrong_page', 'Пожалуйста, введите положительное число')
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
    password = forms.CharField(widget=forms.PasswordInput, required=False, label='Пароль')
    password_check = forms.CharField(widget=forms.PasswordInput, required=False, label='Повторите пароль')
    username = forms.CharField(min_length=3, required=False, label='Никнейм')
    last_name = forms.CharField(min_length=2, required=False, label='Фамилия')
    first_name = forms.CharField(min_length=2, required=False, label='Имя')

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'last_name', 'first_name']

        labels = {'email': 'Почта'}

    def clean_username(self):
        new_username = self.cleaned_data['username']
        existing_user = User.objects.filter(username=new_username).exclude(pk=self.instance.pk).first()
        if existing_user:
            raise ValidationError("Пользователь с таким никнеймом уже существует. Выберите другой ник")
        return new_username

    def clean_email(self):
        new_email = self.cleaned_data['email']
        if new_email:
            existing_user = User.objects.filter(email=new_email).exclude(pk=self.instance.pk).first()
            if existing_user:
                raise ValidationError("Пользователь с такой почтой уже существует")

        return new_email

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        password_check = cleaned_data.get("password_check")

        if password and password_check and password != password_check:
            raise forms.ValidationError("Пароли не совпадают")

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
        print("yes")
        return user

class ProfileSettingsForm(forms.ModelForm):
    avatar = forms.ImageField(required=False)

    class Meta:
        model = models.Profile
        fields = ['avatar']

    def save(self, profile, **kwargs):
        avatar = self.cleaned_data.get('avatar')
        if avatar:
            profile.avatar = avatar
            profile.save()
            return profile
