from django.urls import path
from . import views

app_name = 'eco_tasks'

urlpatterns = [
    path('', views.task_categories, name='categories'),
    path('list/', views.task_list, name='list'),
    path('category/<int:category_id>/', views.task_list, name='category_list'),
    path('task/<int:task_id>/', views.task_detail, name='detail'),
    path('task/<int:task_id>/start/', views.start_task, name='start'),
    path('task/<int:task_id>/work/', views.work_on_task, name='work_on_task'),
    path('task/<int:task_id>/submit/', views.submit_task, name='submit'),
    path('my-tasks/', views.my_tasks, name='my_tasks'),
    path('challenges/', views.challenges, name='challenges'),
    path('challenge/<int:challenge_id>/', views.challenge_detail, name='challenge_detail'),
    path('challenge/<int:challenge_id>/join/', views.join_challenge, name='join_challenge'),
]
