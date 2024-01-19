# Generated by Django 5.0.1 on 2024-01-17 20:30

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='Page',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('number', models.ImageField(upload_to='')),
                ('text', models.CharField(max_length=400)),
            ],
        ),
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('avatar', models.ImageField(blank=True, default='Hombre.png', null=True, upload_to='avatar/')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Task',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=100)),
                ('description', models.CharField(max_length=300)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='Monitoring.profile')),
            ],
        ),
        migrations.CreateModel(
            name='Realization',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('completed', models.BooleanField(default=False)),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='realizations', to='Monitoring.profile')),
                ('current_page', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='realization', to='Monitoring.page')),
                ('task', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='realizations', to='Monitoring.task')),
            ],
        ),
        migrations.AddField(
            model_name='page',
            name='task',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Monitoring.task'),
        ),
    ]