from django.contrib import auth
from django.contrib.auth import authenticate, login
from django.core.paginator import Paginator
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.decorators.csrf import csrf_protect

from Monitoring import models, forms


# Create your views here.


def index(request):
    tasks = models.Task.objects.all()
    page_obj = paginate(tasks, request)
    return render(request, template_name="index.html", context={'tasks': page_obj})


def create(request):
    return render(request, template_name="create.html")


def task(request, task_id):
    task = models.Task.objects.get(pk=task_id)
    return render(request, template_name="task.html", context={'task': task})


def profile(request, profile_id):
    profile = models.Profile.objects.get(pk=profile_id)
    realizations = models.Realization.objects.filter(author=profile)

    print(realizations)
    return render(request, template_name="profile.html", context={'realizations': realizations, 'profile': profile})


def realization(request, realization_id):
    realization = models.Realization.objects.get(pk=realization_id)
    return render(request, template_name="realization.html", context={'realization': realization})


@csrf_protect
def log_in(request):
    if request.method == "POST":
        login_form = forms.LoginForm(request.POST)
        if login_form.is_valid():
            user = authenticate(request, **login_form.cleaned_data)
            if user is not None:
                login(request, user)
                return redirect(request.GET.get('continue', '/'))
            else:
                login_form.add_error(None, "Wrong username or password")
    else:
        login_form = forms.LoginForm()
    return render(request, "login.html", context={"form": login_form})


@csrf_protect
def signup(request):
    if request.method == 'POST':
        user_form = forms.RegisterForm(request.POST)
        if user_form.is_valid():
            user = user_form.save()
            if user:
                login(request, user)
                return redirect(reverse('index'))
            else:
                user_form.add_error(field=None, error="User saving error")
    else:
        user_form = forms.RegisterForm()
    return render(request, template_name="signup.html", context={'form': user_form})


def logout(request):
    auth.logout(request)
    return redirect(reverse('login'))


def paginate(objects, request, per_page=15):
    paginator = Paginator(objects, per_page)
    page = request.GET.get('page', 1)
    page_obj = paginator.page(page)
    return page_obj
