from rest_framework import viewsets, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from django.db.models import Count, Avg, Sum
from accounts.models import User, UserProfile
from quizzes.models import Quiz, QuizAttempt
from eco_tasks.models import EcoTask, UserTask
from leaderboards.models import GlobalLeaderboard
from rewards.models import EcoTokenTransaction

User = get_user_model()

class UserViewSet(viewsets.ReadOnlyModelViewSet):
    """API endpoint for user data"""
    queryset = User.objects.all()
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        from rest_framework import serializers
        
        class UserSerializer(serializers.ModelSerializer):
            class Meta:
                model = User
                fields = ['id', 'username', 'level', 'total_eco_tokens', 'experience_points']
        
        return UserSerializer

class QuizViewSet(viewsets.ReadOnlyModelViewSet):
    """API endpoint for quiz data"""
    queryset = Quiz.objects.filter(is_active=True)
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        from rest_framework import serializers
        
        class QuizSerializer(serializers.ModelSerializer):
            class Meta:
                model = Quiz
                fields = ['id', 'title', 'description', 'difficulty', 'base_tokens_reward']
        
        return QuizSerializer

class TaskViewSet(viewsets.ReadOnlyModelViewSet):
    """API endpoint for task data"""
    queryset = EcoTask.objects.filter(is_active=True)
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        from rest_framework import serializers
        
        class TaskSerializer(serializers.ModelSerializer):
            class Meta:
                model = EcoTask
                fields = ['id', 'title', 'description', 'difficulty', 'base_tokens_reward']
        
        return TaskSerializer

class LeaderboardViewSet(viewsets.ReadOnlyModelViewSet):
    """API endpoint for leaderboard data"""
    queryset = GlobalLeaderboard.objects.all()
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        from rest_framework import serializers
        
        class LeaderboardSerializer(serializers.ModelSerializer):
            username = serializers.CharField(source='user.username')
            
            class Meta:
                model = GlobalLeaderboard
                fields = ['global_rank', 'username', 'total_score']
        
        return LeaderboardSerializer

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_progress(request):
    """Get current user's progress data"""
    user = request.user
    profile, _ = UserProfile.objects.get_or_create(user=user)
    
    # Recent activity
    recent_quizzes = QuizAttempt.objects.filter(
        user=user, is_completed=True
    ).order_by('-completed_at')[:5]
    
    recent_tasks = UserTask.objects.filter(
        user=user, status='completed'
    ).order_by('-completed_at')[:5]
    
    # Token history
    recent_transactions = EcoTokenTransaction.objects.filter(
        user=user
    ).order_by('-created_at')[:10]
    
    data = {
        'user': {
            'username': user.username,
            'level': user.level,
            'total_tokens': user.total_eco_tokens,
            'experience_points': user.experience_points,
            'level_progress': user.get_level_progress(),
        },
        'stats': {
            'quizzes_completed': profile.quizzes_completed,
            'tasks_completed': profile.tasks_completed,
            'current_streak': profile.streak_days,
            'longest_streak': profile.longest_streak,
            'average_quiz_score': profile.average_quiz_score,
        },
        'recent_activity': {
            'quizzes': [
                {
                    'quiz_title': attempt.quiz.title,
                    'score': attempt.score,
                    'completed_at': attempt.completed_at,
                    'tokens_earned': attempt.tokens_earned
                } for attempt in recent_quizzes
            ],
            'tasks': [
                {
                    'task_title': task.task.title,
                    'completed_at': task.completed_at,
                    'tokens_earned': task.tokens_earned
                } for task in recent_tasks
            ]
        },
        'token_history': [
            {
                'amount': trans.amount,
                'description': trans.description,
                'created_at': trans.created_at,
                'balance_after': trans.balance_after
            } for trans in recent_transactions
        ]
    }
    
    return Response(data)

@api_view(['GET'])
def platform_stats(request):
    """Get overall platform statistics"""
    stats = {
        'total_users': User.objects.count(),
        'active_users_week': User.objects.filter(
            last_login__gte=timezone.now() - timedelta(days=7)
        ).count(),
        'total_quizzes': Quiz.objects.filter(is_active=True).count(),
        'quiz_attempts': QuizAttempt.objects.filter(is_completed=True).count(),
        'total_tasks': EcoTask.objects.filter(is_active=True).count(),
        'completed_tasks': UserTask.objects.filter(status='completed').count(),
        'total_tokens_earned': EcoTokenTransaction.objects.filter(
            transaction_type='earned'
        ).aggregate(Sum('amount'))['amount__sum'] or 0,
        'average_user_level': User.objects.aggregate(Avg('level'))['level__avg'] or 1,
    }
    
    return Response(stats)
