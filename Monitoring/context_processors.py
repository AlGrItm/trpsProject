from .models import Profile, Task


def profiles(request):
    return {'profiles': Profile.objects.all()}


def tasks(request):
    unissued_tasks = Task.objects.get_unissued_tasks()
    return {'unissued_tasks': unissued_tasks}


def authenticated(request):
    return {'authenticated': request.user.is_authenticated}
