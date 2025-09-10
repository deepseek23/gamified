from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Avg, Count, Sum
from django.utils import timezone
from datetime import datetime, timedelta
from .models import (
    LeaderboardType, LeaderboardEntry, GlobalLeaderboard, LocalLeaderboard,
    LeaderboardSeason, SeasonParticipant
)
from accounts.models import User, UserProfile

def leaderboard_home(request):
    """Main leaderboards page showing different categories"""
    # Get active leaderboard types
    global_boards = LeaderboardType.objects.filter(
        is_active=True, 
        scope='global'
    ).order_by('period', 'metric')
    
    local_boards = LeaderboardType.objects.filter(
        is_active=True, 
        scope__in=['country', 'city', 'school']
    ).order_by('scope', 'period')
    
    # Get current season if any
    current_season = LeaderboardSeason.objects.filter(
        is_active=True,
        start_date__lte=timezone.now(),
        end_date__gte=timezone.now()
    ).first()
    
    # Get user's current rankings if logged in
    user_rankings = {}
    if request.user.is_authenticated:
        try:
            global_rank = GlobalLeaderboard.objects.get(user=request.user)
            user_rankings['global'] = global_rank
        except GlobalLeaderboard.DoesNotExist:
            pass
        
        # Get local rankings
        if request.user.city:
            local_city = LocalLeaderboard.objects.filter(
                user=request.user,
                location_type='city',
                location_value=request.user.city
            ).first()
            if local_city:
                user_rankings['city'] = local_city
        
        if request.user.school_name:
            local_school = LocalLeaderboard.objects.filter(
                user=request.user,
                location_type='school',
                location_value=request.user.school_name
            ).first()
            if local_school:
                user_rankings['school'] = local_school
    
    context = {
        'global_boards': global_boards,
        'local_boards': local_boards,
        'current_season': current_season,
        'user_rankings': user_rankings,
    }
    return render(request, 'leaderboards/home.html', context)

def global_leaderboard(request, board_type=None):
    """Display global leaderboard"""
    if board_type:
        leaderboard_type = get_object_or_404(
            LeaderboardType, 
            id=board_type, 
            is_active=True, 
            scope='global'
        )
        
        # Get current period entries
        entries = LeaderboardEntry.objects.filter(
            leaderboard_type=leaderboard_type
        ).select_related('user').order_by('rank')[:50]
        
        # Get user's position if logged in
        user_entry = None
        if request.user.is_authenticated:
            try:
                user_entry = LeaderboardEntry.objects.get(
                    leaderboard_type=leaderboard_type,
                    user=request.user
                )
            except LeaderboardEntry.DoesNotExist:
                pass
        
        context = {
            'leaderboard_type': leaderboard_type,
            'entries': entries,
            'user_entry': user_entry,
        }
        return render(request, 'leaderboards/global_detail.html', context)
    
    else:
        # Show overall global leaderboard
        top_users = GlobalLeaderboard.objects.select_related('user').order_by('global_rank')[:50]
        
        # Get user's global position
        user_global = None
        if request.user.is_authenticated:
            try:
                user_global = GlobalLeaderboard.objects.get(user=request.user)
            except GlobalLeaderboard.DoesNotExist:
                pass
        
        context = {
            'top_users': top_users,
            'user_global': user_global,
        }
        return render(request, 'leaderboards/global.html', context)

def local_leaderboard(request, location_type, location_value=None):
    """Display local leaderboards"""
    if not location_value and request.user.is_authenticated:
        # Auto-detect user's location
        if location_type == 'city':
            location_value = request.user.city
        elif location_type == 'school':
            location_value = request.user.school_name
        elif location_type == 'country':
            location_value = request.user.country
    
    if not location_value:
        messages.error(request, "Location not specified")
        return redirect('leaderboards:home')
    
    # Get local leaderboard entries
    entries = LocalLeaderboard.objects.filter(
        location_type=location_type,
        location_value=location_value,
        period_type='all_time'  # Default to all-time
    ).select_related('user').order_by('rank')[:50]
    
    # Get user's position
    user_entry = None
    if request.user.is_authenticated:
        try:
            user_entry = LocalLeaderboard.objects.get(
                location_type=location_type,
                location_value=location_value,
                user=request.user,
                period_type='all_time'
            )
        except LocalLeaderboard.DoesNotExist:
            pass
    
    context = {
        'location_type': location_type,
        'location_value': location_value,
        'entries': entries,
        'user_entry': user_entry,
    }
    return render(request, 'leaderboards/local.html', context)

def seasonal_leaderboard(request, season_id=None):
    """Display seasonal competitions"""
    if season_id:
        season = get_object_or_404(LeaderboardSeason, id=season_id, is_active=True)
        
        # Get participants
        participants = SeasonParticipant.objects.filter(
            season=season
        ).select_related('user').order_by('season_rank')[:50]
        
        # Get user's participation
        user_participation = None
        if request.user.is_authenticated:
            try:
                user_participation = SeasonParticipant.objects.get(
                    season=season,
                    user=request.user
                )
            except SeasonParticipant.DoesNotExist:
                pass
        
        context = {
            'season': season,
            'participants': participants,
            'user_participation': user_participation,
            'is_running': season.is_running(),
        }
        return render(request, 'leaderboards/season_detail.html', context)
    
    else:
        # Show all seasons
        active_seasons = LeaderboardSeason.objects.filter(
            is_active=True
        ).order_by('-start_date')
        
        current_seasons = [s for s in active_seasons if s.is_running()]
        upcoming_seasons = [s for s in active_seasons if s.start_date > timezone.now()]
        past_seasons = [s for s in active_seasons if s.end_date < timezone.now()]
        
        context = {
            'current_seasons': current_seasons,
            'upcoming_seasons': upcoming_seasons,
            'past_seasons': past_seasons[:5],  # Show last 5 past seasons
        }
        return render(request, 'leaderboards/seasons.html', context)

@login_required
def join_season(request, season_id):
    """Join a seasonal competition"""
    season = get_object_or_404(LeaderboardSeason, id=season_id, is_active=True)
    
    if not season.is_running():
        messages.error(request, "Season is not currently active")
        return redirect('leaderboards:seasonal', season_id=season_id)
    
    participant, created = SeasonParticipant.objects.get_or_create(
        user=request.user,
        season=season
    )
    
    if created:
        messages.success(request, f"Joined {season.name}!")
    else:
        messages.info(request, "You're already participating in this season")
    
    return redirect('leaderboards:seasonal', season_id=season_id)

def quiz_leaderboards(request):
    """Show quiz-specific leaderboards"""
    from quizzes.models import QuizAttempt, Quiz
    
    # Top quiz performers (all time)
    top_quiz_performers = User.objects.annotate(
        avg_score=Avg('quiz_attempts__score'),
        total_quizzes=Count('quiz_attempts', filter=Q(quiz_attempts__is_completed=True))
    ).filter(
        total_quizzes__gte=3  # At least 3 completed quizzes
    ).order_by('-avg_score')[:20]
    
    # Recent perfect scores
    perfect_scores = QuizAttempt.objects.filter(
        score=100.0,
        is_completed=True
    ).select_related('user', 'quiz').order_by('-completed_at')[:10]
    
    # Most active quiz takers this week
    week_ago = timezone.now() - timedelta(days=7)
    weekly_active = User.objects.annotate(
        weekly_quizzes=Count('quiz_attempts', filter=Q(
            quiz_attempts__completed_at__gte=week_ago,
            quiz_attempts__is_completed=True
        ))
    ).filter(weekly_quizzes__gt=0).order_by('-weekly_quizzes')[:15]
    
    context = {
        'top_quiz_performers': top_quiz_performers,
        'perfect_scores': perfect_scores,
        'weekly_active': weekly_active,
    }
    return render(request, 'leaderboards/quiz_leaderboards.html', context)

def task_leaderboards(request):
    """Show task-specific leaderboards"""
    from eco_tasks.models import UserTask
    
    # Top task completers
    top_task_performers = User.objects.annotate(
        completed_tasks=Count('eco_tasks', filter=Q(eco_tasks__status='completed'))
    ).filter(completed_tasks__gt=0).order_by('-completed_tasks')[:20]
    
    # Recent task completions
    recent_completions = UserTask.objects.filter(
        status='completed'
    ).select_related('user', 'task').order_by('-completed_at')[:10]
    
    # Most active this month
    month_ago = timezone.now() - timedelta(days=30)
    monthly_active = User.objects.annotate(
        monthly_tasks=Count('eco_tasks', filter=Q(
            eco_tasks__completed_at__gte=month_ago,
            eco_tasks__status='completed'
        ))
    ).filter(monthly_tasks__gt=0).order_by('-monthly_tasks')[:15]
    
    context = {
        'top_task_performers': top_task_performers,
        'recent_completions': recent_completions,
        'monthly_active': monthly_active,
    }
    return render(request, 'leaderboards/task_leaderboards.html', context)
