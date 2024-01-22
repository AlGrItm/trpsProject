from django.contrib.auth.models import User
from django.db import models

# Create your models here.


class Profile(models.Model):
    avatar = models.ImageField(null=True, blank=True, default='static/Hombre.png', upload_to='static/Images/')
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)

    def __str__(self):
        return f'{self.user.first_name}  {self.user.last_name}'


class TaskManager(models.Manager):
    def get_recent_tasks(self, count=15):
        return self.order_by('-created_at')[:count]


class Task(models.Model):
    title = models.CharField(max_length=100)
    author = models.ForeignKey('Profile', on_delete=models.PROTECT)
    description = models.CharField(max_length=300)
    created_at = models.DateTimeField(auto_now_add=True)
    pages_number = models.IntegerField()
    objects = TaskManager()

    def __str__(self):
        return self.title


class Page(models.Model):
    number = models.IntegerField()
    correct_page = models.IntegerField(default=1)
    wrong_page = models.IntegerField(null=True, blank=True, default=None)
    task = models.ForeignKey('Task', on_delete=models.CASCADE, related_name='pages')
    text = models.CharField(max_length=400)

    class Meta:
        unique_together = ('task', 'number')

    def __str__(self):
        return f'{self.task.title}: {self.number}'


class Realization(models.Model):
    author = models.ForeignKey('Profile', on_delete=models.PROTECT, related_name='realizations')
    completed = models.BooleanField(default=False)
    current_page = models.ForeignKey('Page', on_delete=models.CASCADE, related_name='realizations')
    task = models.ForeignKey('Task', on_delete=models.CASCADE, related_name='realizations')

    def __str__(self):
        return f'{self.author.user.last_name} {self.author.user.first_name}: {self.task.title}'
