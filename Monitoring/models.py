from django.contrib.auth.models import User
from django.db import models

# Create your models here.


class Profile(models.Model):
    avatar = models.ImageField(null=True, blank=True, default='Hombre.png', upload_to='avatar/')
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)

    def __str__(self):
        return f'{self.user.first_name}  {self.user.last_name}'


class TaskManager(models.Manager):
    def get_recent_tasks(self, count=7):
        return self.order_by('-created_at')[:count]


class Task(models.Model):
    title = models.CharField(max_length=100)
    author = models.ForeignKey('Profile', on_delete=models.PROTECT)
    description = models.CharField(max_length=300)
    created_at = models.DateTimeField(auto_now_add=True)
    objects = TaskManager()

    def __str__(self):
        return self.title


class Page(models.Model):
    number = models.IntegerField()
    task = models.ForeignKey('Task', on_delete=models.CASCADE)
    text = models.CharField(max_length=400)

    def __str__(self):
        return f'{self.task.title}: {self.number}'


class Realization(models.Model):
    author = models.ForeignKey('Profile', on_delete=models.PROTECT, related_name='realizations')
    completed = models.BooleanField(default=False)
    current_page = models.OneToOneField('Page', on_delete=models.CASCADE, related_name='realization')
    task = models.ForeignKey('Task', on_delete=models.CASCADE, related_name='realizations')

    def __str__(self):
        return f'{self.author.user.last_name} {self.author.user.first_name}: {self.task.title}'
