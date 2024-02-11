from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone
from django.db.models import Count
from datetime import datetime


# Create your models here.


class ProfileManager(models.Manager):
    def top_profiles_this_month(self):
        current_month = datetime.now().month
        current_year = datetime.now().year
        return self.annotate(
            solved_tasks=Count('realizations', filter=models.Q(realizations__completed=True,
                                                               realizations__completed_date__month=current_month,
                                                               realizations__completed_date__year=current_year,
                                                               realizations__task__deadline__gt=models.F('realizations__completed_date')))
        ).order_by('-solved_tasks')[:3]


class Profile(models.Model):
    avatar = models.ImageField(null=True, blank=True, default='static/Images/Hombre.png', upload_to='static/Images/')
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    objects = ProfileManager()

    def __str__(self):
        return f'{self.user.first_name}  {self.user.last_name}'


class TaskManager(models.Manager):
    def get_unissued_tasks(self):
        return self.filter(issued=False)[:15]

    def user_tasks(self, user):
        return self.filter(realizations__author__user=user).distinct()

    def completed_tasks(self):
        return self.filter(pages__realizations__completed=True).distinct()

    def uncompleted_tasks(self):
        return self.filter(pages__realizations__completed=False).distinct()


class Task(models.Model):
    title = models.CharField(max_length=1000)
    author = models.ForeignKey('Profile', on_delete=models.PROTECT)
    description = models.CharField(max_length=1000)
    created_at = models.DateTimeField(auto_now_add=True)
    pages_number = models.IntegerField()
    deadline = models.DateField(default=timezone.now)
    issued = models.BooleanField(default=False)
    objects = TaskManager()

    def __str__(self):
        return self.title


class Page(models.Model):
    number = models.IntegerField()
    correct_page = models.IntegerField(default=1)
    wrong_page = models.IntegerField(null=True, blank=True, default=None)
    task = models.ForeignKey('Task', on_delete=models.CASCADE, related_name='pages')
    text = models.CharField(max_length=1000)

    class Meta:
        unique_together = ('task', 'number')

    def __str__(self):
        return f'{self.task.title}: {self.number}'


class RealizationManager(models.Manager):
    def get_deadlines_in_order(self):
        return self.filter(completed=False).order_by('task__deadline')

    def uncompleted_realizations(self, user):
        return self.filter(author__user=user, completed=False)

    def user_realizations(self, user):
        return self.filter(author__user=user)


class Realization(models.Model):
    author = models.ForeignKey('Profile', on_delete=models.PROTECT, related_name='realizations')
    completed = models.BooleanField(default=False)
    completed_date = models.DateField(default=timezone.now, null=True, blank=True)
    current_page = models.ForeignKey('Page', on_delete=models.CASCADE, related_name='realizations')
    task = models.ForeignKey('Task', on_delete=models.CASCADE, related_name='realizations')
    objects = RealizationManager()

    def __str__(self):
        return f'{self.author.user.last_name} {self.author.user.first_name}: {self.task.title}'
