from django.contrib import admin
from django.urls import path

from Monitoring import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index, name='index'),
    path('create/', views.create, name='create'),
    path('task/<task_id>/', views.task, name='task'),
    path('profile/<profile_id>/', views.profile, name='profile'),
    path('realization/<realization_id>/', views.realization, name='realization'),
    path('logout/', views.logout, name='logout'),
    path('login/', views.log_in, name='login'),
    path('signup/', views.signup, name='signup'),
    path('create_page/<task_id>/<int:page_number>/', views.create_page, name='create_page'),
    path('fill/<realization_id>', views.fill, name='fill'),
    path('begin_fill/', views.begin_fill, name='begin_fill'),
    path('settings/', views.settings, name='settings'),
    path('profiles/<task_id>', views.profiles, name='profiles'),
    path('edit/<task_id>', views.edit, name='edit'),
    path('statistic', views.statistic, name='statistic'),
    path('schedule', views.schedule, name='schedule'),
]
