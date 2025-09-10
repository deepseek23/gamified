from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'users', views.UserViewSet)
router.register(r'quizzes', views.QuizViewSet)
router.register(r'tasks', views.TaskViewSet)
router.register(r'leaderboards', views.LeaderboardViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('auth/', include('rest_framework.urls')),
    path('stats/', views.platform_stats, name='platform_stats'),
    path('user-progress/', views.user_progress, name='user_progress'),
]
