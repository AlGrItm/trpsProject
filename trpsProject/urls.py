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
]
