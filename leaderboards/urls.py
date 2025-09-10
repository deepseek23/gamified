from django.urls import path
from . import views

app_name = 'leaderboards'

urlpatterns = [
    path('', views.leaderboard_home, name='home'),
    path('global/', views.global_leaderboard, name='global'),
    path('global/<int:board_type>/', views.global_leaderboard, name='global_detail'),
    path('local/<str:location_type>/', views.local_leaderboard, name='local'),
    path('local/<str:location_type>/<str:location_value>/', views.local_leaderboard, name='local_detail'),
    path('seasons/', views.seasonal_leaderboard, name='seasons'),
    path('season/<int:season_id>/', views.seasonal_leaderboard, name='seasonal'),
    path('season/<int:season_id>/join/', views.join_season, name='join_season'),
    path('quizzes/', views.quiz_leaderboards, name='quiz_leaderboards'),
    path('tasks/', views.task_leaderboards, name='task_leaderboards'),
]
