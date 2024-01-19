from .models import Profile, Task


def profiles(request):
    return {'profiles': Profile.objects.all()}


def tasks(request):
    recent_tasks = Task.objects.get_recent_tasks()
    return {'recent_tasks': recent_tasks}


def authenticated(request):
    return {'authenticated': request.user.is_authenticated}
