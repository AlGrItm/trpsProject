from django.contrib import auth
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.views.decorators.csrf import csrf_protect
from django.http import JsonResponse
from django.contrib import messages


from Monitoring import models, forms


# Create your views here.


def is_admin(user):
    return user.is_authenticated and user.is_staff


def index(request):
    if not request.user.is_authenticated:
        return redirect(reverse('login'))
    tasks = models.Task.objects.all()
    page_obj = paginate(tasks, request)
    return render(request, template_name="index.html", context={'page_obj': page_obj})


def create(request):
    if not is_admin(request.user):
        return redirect('index')
    if request.method == 'POST':
        form = forms.CreateTask(request.POST, author=request.user.profile)
        if form.is_valid():
            task = form.save()
            first_page = task.pages.first()
            return redirect(reverse('create_page', kwargs={'task_id': task.id, 'page_number': first_page.number}))
    else:
        form = forms.CreateTask(author=request.user)
    return render(request, template_name="create.html", context={'form': form})


def create_page(request, task_id, page_number):
    if not is_admin(request.user):
        return redirect('index')
    task = get_object_or_404(models.Task, pk=task_id)
    if request.method == 'POST':
        form = forms.CreatePage(request.POST)
        if form.is_valid():
            page = form.save(task=task, number=page_number)
            if page_number < task.pages.count():
                next_page_number = page_number + 1
                return redirect(reverse('create_page', kwargs={'task_id': task.id, 'page_number': next_page_number}))
            else:
                return redirect('index')
    else:
        form = forms.CreatePage()
    return render(request, template_name="create_page.html", context={'form': form, 'task': task, 'page_number': page_number})


def settings(request):
    if not request.user.is_authenticated:
        return redirect(reverse('login'))
    user = request.user
    profile = get_object_or_404(models.Profile, user=user)
    if request.method == 'POST':
        settings_form = forms.SettingsForm(request.POST, request.FILES, instance=profile)
        profile_form = forms.ProfileSettingsForm(request.POST, request.FILES, instance=profile)
        if settings_form.is_valid() and profile_form.is_valid():
            settings_form.save(user=user, request=request)
            profile_form.save(profile=profile)
            return redirect(reverse('settings'))
    else:
        initial_data = {'username': user.username, 'last_name': user.last_name, 'first_name': user.first_name}
        settings_form = forms.SettingsForm(initial=initial_data, instance=profile)
    return render(request, template_name="settings.html", context={'form': settings_form})


def task(request, task_id):
    if not request.user.is_authenticated:
        return redirect(reverse('login'))
    task = models.Task.objects.get(pk=task_id)
    return render(request, template_name="task.html", context={'task': task})


def profile(request, profile_id):
    if not request.user.is_authenticated:
        return redirect(reverse('login'))
    profile = models.Profile.objects.get(pk=profile_id)
    realizations = models.Realization.objects.filter(author=profile)
    page_obj = paginate(realizations, request, 4)

    return render(request, template_name="profile.html", context={'page_obj': page_obj, 'profile': profile})


def realization(request, realization_id):
    if not request.user.is_authenticated:
        return redirect(reverse('login'))
    realization = models.Realization.objects.get(pk=realization_id)
    return render(request, template_name="realization.html", context={'realization': realization})


def fill(request, realization_id):
    if not request.user.is_authenticated:
        return redirect(reverse('login'))
    realization = models.Realization.objects.get(pk=realization_id)
    if not realization.author == request.user.profile:
        return redirect('index')

    task = realization.task
    current_page = realization.current_page

    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'correct':
            next_page_number = current_page.correct_page
            if next_page_number <= task.pages_number:
                realization.current_page = task.pages.get(number=next_page_number)
                realization.save()
            else:
                realization.completed = True
                realization.save()
                return redirect('index')
        elif action == 'wrong':
            next_page_number = current_page.wrong_page
            realization.current_page = task.pages.get(number=next_page_number)
            realization.save()

    return render(request, 'fill.html', {'realization': realization, 'current_page': current_page})


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


def begin_fill(request):
    task_id = request.POST.get('task_id')
    task = models.Task.objects.get(id=task_id)
    page = task.pages.first()
    realization = models.Realization.objects.create(
        author=request.user.profile,
        current_page=page,
        task=task
    )
    response_data = {'redirect_url': reverse('fill', kwargs={'realization_id': realization.id})}
    return JsonResponse(response_data)
