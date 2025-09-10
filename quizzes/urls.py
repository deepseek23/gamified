from django.urls import path
from . import views

app_name = 'quizzes'

urlpatterns = [
    path('', views.quiz_categories, name='categories'),
    path('list/', views.quiz_list, name='list'),
    path('category/<int:category_id>/', views.quiz_list, name='category_list'),
    path('quiz/<int:quiz_id>/', views.quiz_detail, name='detail'),
    path('quiz/<int:quiz_id>/start/', views.start_quiz, name='start'),
    path('take/<int:attempt_id>/', views.take_quiz, name='take_quiz'),
    path('submit/<int:attempt_id>/', views.submit_answer, name='submit_answer'),
    path('complete/<int:attempt_id>/', views.complete_quiz, name='complete'),
    path('leaderboard/<int:quiz_id>/', views.quiz_leaderboard, name='leaderboard'),
]
