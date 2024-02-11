from django.contrib import auth
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from datetime import datetime, timedelta
import locale
from django.utils import timezone
from django.views.decorators.csrf import csrf_protect
from django.http import JsonResponse, HttpResponseRedirect, HttpResponse
from django.contrib import messages

from Monitoring import models, forms, times


def is_admin(user):
    return user.is_authenticated and user.is_staff


def index(request):
    if not request.user.is_authenticated:
        return redirect(reverse('login'))

    if is_admin(request.user):
        realizations = models.Realization.objects.get_deadlines_in_order()
    else:
        realizations = models.Realization.objects.uncompleted_realizations(request.user)

    today = datetime.now().date()
    deadline_soon = today + timedelta(days=7)
    page_obj = paginate(realizations, request, 5)
    return render(request, template_name="index.html",
                  context={'page_obj': page_obj, 'today': today, 'deadline_soon': deadline_soon})


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


def edit(request, task_id):
    if not is_admin(request.user):
        return redirect('index')

    task = get_object_or_404(models.Task, id=task_id)

    if request.method == 'POST':
        form = forms.EditTaskForm(request.POST, instance=task)
        if form.is_valid():
            form.save()
            return redirect('index')
    else:
        form = forms.EditTaskForm(instance=task)

    return render(request, 'edit.html', {'form': form, 'task': task})


def create_page(request, task_id, page_number):
    if not is_admin(request.user):
        return redirect('index')

    task = get_object_or_404(models.Task, pk=task_id)
    pages_number = task.pages_number

    if request.method == 'POST':
        form = forms.CreatePage(request.POST)
        if form.is_valid():
            page = form.save(task=task, number=page_number)
            if page_number < pages_number:
                next_page_number = page_number + 1
                return redirect(reverse('create_page', kwargs={'task_id': task.id, 'page_number': next_page_number}))
            else:
                return JsonResponse({'redirect_url': reverse('index')})
    else:
        form = forms.CreatePage()

    context = {
        'form': form,
        'task': task,
        'page_number': page_number,
        'pages_number': pages_number,
    }

    return render(request, template_name="create_page.html", context=context)


def profiles(request, task_id):
    if not is_admin(request.user):
        return redirect('index')

    task = models.Task.objects.get(pk=task_id)
    profiles = models.Profile.objects.all()

    if request.method == 'POST':
        profile_id = request.POST.get('selected_profile')
        if profile_id:
            task.issued = True
            task.save()
            current_page = task.pages.first()
            author = models.Profile.objects.get(pk=profile_id)
            realization = models.Realization.objects.create(author=author, task=task, current_page=current_page)
            return redirect(reverse('index'))

    return render(request, template_name="profiles.html", context={'profiles': profiles, 'task': task})


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
            messages.success(request, 'Изменения сохранены успешно.')
            return redirect(reverse('settings'))
    else:
        if user.email:
            email = user.email
        else:
            email = ''

        initial_data = {
            'username': user.username,
            'last_name': user.last_name,
            'first_name': user.first_name,
            'email': email
        }

        settings_form = forms.SettingsForm(initial=initial_data, instance=profile)

    return render(request, template_name="settings.html", context={'form': settings_form})


def task(request, task_id):
    if not request.user.is_authenticated:
        return redirect(reverse('login'))

    task = models.Task.objects.get(pk=task_id)
    realization = task.realizations.first()
    today = datetime.now().date()
    deadline_soon = today + timedelta(days=7)
    if realization:
        percent = int((realization.current_page.number - 1) / task.pages_number * 100)
    else:
        percent = 0
    context = {
        'task': task,
        'realization': realization,
        'today': today,
        'deadline_soon': deadline_soon,
        'percent': percent,
    }

    return render(request, template_name="task.html", context=context)


def profile(request, profile_id):
    if not request.user.is_authenticated:
        return redirect(reverse('login'))

    today = datetime.now().date()
    deadline_soon = today + timedelta(days=7)
    profile = models.Profile.objects.get(pk=profile_id)
    realizations = models.Realization.objects.filter(author=profile)
    page_obj = paginate(realizations, request, 4)

    if not request.user.is_staff and request.user.profile != profile:
        return HttpResponseRedirect(request.META.get('HTTP_REFERER', reverse('index')))

    context = {
        'page_obj': page_obj,
        'profile': profile,
        'today': today,
        'deadline_soon': deadline_soon
    }

    return render(request, template_name="profile.html", context=context)


def schedule(request):
    if not request.user.is_authenticated:
        return redirect(reverse('login'))

    if not is_admin(request.user):
        return redirect(reverse('index'))

    filter = request.GET.get('filter', 'all')
    user_id = request.GET.get('user_id')
    tasks = models.Task.objects.all()
    today = datetime.now().date()

    if filter == 'all':
        tasks = models.Task.objects.all()
    elif filter == 'assigned':
        tasks = models.Task.objects.filter(realizations__isnull=False).distinct()
    elif filter == 'completed':
        tasks = models.Task.objects.filter(realizations__completed=True).distinct()
    elif filter == 'uncompleted':
        tasks = models.Task.objects.filter(realizations__completed=False).distinct()
    elif filter == 'overdue':
        tasks = models.Task.objects.filter(
            deadline__lt=today,
            realizations__completed=False
        ).distinct()
    elif filter == 'user':
        tasks = models.Task.objects.filter(realizations__author=user_id)

    date = request.GET.get('date')

    if date == 'this_week':
        days = times.this_week()
    elif date == 'next_week':
        days = times.next_week()
    elif date == 'this_month':
        days = times.this_month()
    elif date == 'next_month':
        days = times.next_month()
    elif date == 'half_year':
        days = times.half_year()
    elif date == 'align':
        days = times.get_days(tasks)
    elif date == 'custom':
        days = times.get_custom_days(request.GET.get('startDate'), request.GET.get('endDate'))
    else:
        days = times.get_days(tasks)

    users = models.Profile.objects.all()

    context = {
        'tasks': tasks,
        'days': days,
        'today': today,
        'filter': filter,
        'date': date,
        'users': users,
        'selected_user_id': user_id
    }

    return render(request, 'schedule.html', context)


def statistic(request):
    if not request.user.is_authenticated:
        return redirect(reverse('login'))

    if not is_admin(request.user):
        return redirect(reverse('index'))

    filter = request.GET.get('filter', 'all')
    user_id = request.GET.get('user_id')

    tasks = []

    if filter == 'all':
        tasks = models.Task.objects.all()
    elif filter == 'issued':
        tasks = models.Task.objects.filter(issued=True)
    elif filter == 'unissued':
        tasks = models.Task.objects.filter(issued=False)
    elif filter == 'completed':
        tasks = models.Task.objects.completed_tasks()
    elif filter == 'uncompleted':
        tasks = models.Task.objects.uncompleted_tasks()
    elif filter == 'user' and user_id:
        selected_user = models.Profile.objects.get(pk=user_id)
        tasks = models.Task.objects.user_tasks(selected_user)

    users = models.Profile.objects.all()
    selected_user_id = int(user_id) if user_id else None

    context = {
        'tasks': tasks,
        'filter': filter,
        'users': users,
        'selected_user_id': user_id,
    }
    return render(request, template_name="statistic.html", context=context)


def top(request):
    if not request.user.is_authenticated:
        return redirect(reverse('login'))
    top_profiles = models.Profile.objects.top_profiles_this_month()

    plural_tasks = []
    for profile in top_profiles:
        plural_tasks.append(get_task_plural_form(profile.solved_tasks))

    locale.setlocale(locale.LC_TIME, 'ru_RU.UTF-8')
    month_name = datetime.now().strftime('%B')

    context = {
        'top_profiles': top_profiles,
        'plural_tasks': plural_tasks,
        'month': month_name,

    }

    return render(request, template_name="top.html", context=context)


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
                realization.task.completed_date = datetime.now().date()
                realization.save()
                return redirect('index')
        elif action == 'wrong':
            next_page_number = current_page.wrong_page
            realization.current_page = task.pages.get(number=next_page_number)
            realization.save()

    return render(request, 'fill.html', {'realization': realization})


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
        login_form = forms.LoginForm(initial={'username': '', 'password': ''})

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
        user_form = forms.RegisterForm(initial={
            'username': '',
            'first_name': '',
            'last_name': '',
        })

    return render(request, template_name="signup.html", context={'form': user_form})


def logout(request):
    auth.logout(request)
    return redirect(reverse('login'))


def paginate(objects, request, per_page=15):
    if objects is None:
        return None
    paginator = Paginator(objects, per_page)
    page = request.GET.get('page', 1)
    try:
        page_obj = paginator.page(page)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)
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
    if realization:
        task.issued = True
        task.save()
    response_data = {'redirect_url': reverse('fill', kwargs={'realization_id': realization.id})}
    return JsonResponse(response_data)


def get_task_plural_form(number):
    if number % 10 == 1 and number % 100 != 11:
        return 'задание'
    elif 2 <= number % 10 <= 4 and (number % 100 < 10 or number % 100 >= 20):
        return 'задания'
    else:
        return 'заданий'
