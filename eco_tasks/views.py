from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from django.utils import timezone
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .models import (
    TaskCategory, EcoTask, UserTask, TaskSubmissionItem,
    TaskChallenge, UserChallenge
)
from rewards.views import award_tokens
from accounts.models import UserProfile

def task_categories(request):
    """Display all task categories"""
    categories = TaskCategory.objects.filter(is_active=True).prefetch_related('tasks')
    
    context = {
        'categories': categories,
    }
    return render(request, 'eco_tasks/categories.html', context)

def task_list(request, category_id=None):
    """Display tasks, optionally filtered by category"""
    tasks = EcoTask.objects.filter(is_active=True).select_related('category')
    
    if category_id:
        category = get_object_or_404(TaskCategory, id=category_id, is_active=True)
        tasks = tasks.filter(category=category)
        context = {'tasks': tasks, 'category': category}
    else:
        context = {'tasks': tasks}
    
    # Add user progress info if logged in
    if request.user.is_authenticated:
        user_tasks = UserTask.objects.filter(user=request.user).values('task_id', 'status')
        user_task_status = {ut['task_id']: ut['status'] for ut in user_tasks}
        
        task_progress = []
        for task in tasks:
            progress_info = {
                'task': task,
                'status': user_task_status.get(task.id, 'not_started'),
                'can_access': task.min_level_required <= request.user.level,
            }
            task_progress.append(progress_info)
        
        context['task_progress'] = task_progress
    
    return render(request, 'eco_tasks/task_list.html', context)

@login_required
def task_detail(request, task_id):
    """Display task details"""
    task = get_object_or_404(EcoTask, id=task_id, is_active=True)
    
    # Get or create user task
    user_task, created = UserTask.objects.get_or_create(
        user=request.user,
        task=task
    )
    
    # Check if user can access this task
    can_start, message = user_task.can_start()
    
    context = {
        'task': task,
        'user_task': user_task,
        'can_start': can_start,
        'access_message': message,
    }
    return render(request, 'eco_tasks/task_detail.html', context)

@login_required
@require_POST
def start_task(request, task_id):
    """Start a task"""
    task = get_object_or_404(EcoTask, id=task_id, is_active=True)
    user_task, created = UserTask.objects.get_or_create(
        user=request.user,
        task=task
    )
    
    if user_task.start_task():
        messages.success(request, f"Started task: {task.title}")
        return redirect('eco_tasks:work_on_task', task_id=task_id)
    else:
        messages.error(request, "Cannot start this task")
        return redirect('eco_tasks:detail', task_id=task_id)

@login_required
def work_on_task(request, task_id):
    """Work on task - show submission form"""
    task = get_object_or_404(EcoTask, id=task_id, is_active=True)
    user_task = get_object_or_404(UserTask, user=request.user, task=task)
    
    if user_task.status not in ['in_progress', 'rejected']:
        messages.error(request, "Task is not in progress")
        return redirect('eco_tasks:detail', task_id=task_id)
    
    # Get submission items for checklist tasks
    submission_items = TaskSubmissionItem.objects.filter(user_task=user_task)
    
    context = {
        'task': task,
        'user_task': user_task,
        'submission_items': submission_items,
    }
    return render(request, 'eco_tasks/work_on_task.html', context)

@login_required
@require_POST
def submit_task(request, task_id):
    """Submit task for review"""
    task = get_object_or_404(EcoTask, id=task_id, is_active=True)
    user_task = get_object_or_404(UserTask, user=request.user, task=task)
    
    if user_task.status != 'in_progress':
        messages.error(request, "Task is not in progress")
        return redirect('eco_tasks:detail', task_id=task_id)
    
    # Handle submission based on verification method
    if task.verification_method == 'text':
        user_task.submission_text = request.POST.get('submission_text', '')
    elif task.verification_method == 'photo':
        if 'submission_image' in request.FILES:
            user_task.submission_image = request.FILES['submission_image']
        user_task.submission_text = request.POST.get('submission_text', '')
    elif task.verification_method == 'video':
        if 'submission_video' in request.FILES:
            user_task.submission_video = request.FILES['submission_video']
        user_task.submission_text = request.POST.get('submission_text', '')
    
    user_task.status = 'submitted'
    user_task.submitted_at = timezone.now()
    
    # If task doesn't require approval, auto-complete it
    if not task.requires_approval:
        user_task.status = 'completed'
        user_task.completed_at = timezone.now()
        user_task.tokens_earned = task.base_tokens_reward
        user_task.experience_gained = task.experience_points
        
        # Award tokens and experience
        award_tokens(
            user=request.user,
            source='task_completion',
            amount=task.base_tokens_reward,
            description=f"Completed task: {task.title}",
            task_id=task.id
        )
        
        request.user.add_experience(task.experience_points)
        
        # Update profile
        profile, created = UserProfile.objects.get_or_create(user=request.user)
        profile.tasks_completed += 1
        profile.update_streak()
        profile.save()
        
        messages.success(request, f"Task completed! Earned {task.base_tokens_reward} tokens!")
    else:
        messages.success(request, "Task submitted for review!")
    
    user_task.save()
    return redirect('eco_tasks:my_tasks')

@login_required
def my_tasks(request):
    """Display user's tasks"""
    user_tasks = UserTask.objects.filter(user=request.user).select_related('task').order_by('-created_at')
    
    # Group by status
    tasks_by_status = {
        'in_progress': [],
        'submitted': [],
        'completed': [],
        'rejected': [],
    }
    
    for user_task in user_tasks:
        if user_task.status in tasks_by_status:
            tasks_by_status[user_task.status].append(user_task)
    
    context = {
        'tasks_by_status': tasks_by_status,
    }
    return render(request, 'eco_tasks/my_tasks.html', context)

def challenges(request):
    """Display available challenges"""
    active_challenges = TaskChallenge.objects.filter(is_active=True).order_by('-start_date')
    
    # Add user participation info if logged in
    if request.user.is_authenticated:
        user_challenges = UserChallenge.objects.filter(
            user=request.user
        ).values('challenge_id', 'status', 'tasks_completed')
        
        user_challenge_data = {
            uc['challenge_id']: {
                'status': uc['status'],
                'tasks_completed': uc['tasks_completed']
            } for uc in user_challenges
        }
        
        challenge_info = []
        for challenge in active_challenges:
            info = {
                'challenge': challenge,
                'user_data': user_challenge_data.get(challenge.id),
                'is_available': challenge.is_available(),
            }
            challenge_info.append(info)
        
        context = {'challenge_info': challenge_info}
    else:
        context = {'challenges': active_challenges}
    
    return render(request, 'eco_tasks/challenges.html', context)

@login_required
@require_POST
def join_challenge(request, challenge_id):
    """Join a challenge"""
    challenge = get_object_or_404(TaskChallenge, id=challenge_id, is_active=True)
    
    if not challenge.is_available():
        messages.error(request, "Challenge is not available")
        return redirect('eco_tasks:challenges')
    
    user_challenge, created = UserChallenge.objects.get_or_create(
        user=request.user,
        challenge=challenge
    )
    
    if created:
        messages.success(request, f"Joined challenge: {challenge.title}")
    else:
        messages.info(request, "You're already participating in this challenge")
    
    return redirect('eco_tasks:challenge_detail', challenge_id=challenge_id)

@login_required
def challenge_detail(request, challenge_id):
    """Display challenge details"""
    challenge = get_object_or_404(TaskChallenge, id=challenge_id, is_active=True)
    
    # Get user's participation
    user_challenge = None
    if request.user.is_authenticated:
        try:
            user_challenge = UserChallenge.objects.get(
                user=request.user,
                challenge=challenge
            )
        except UserChallenge.DoesNotExist:
            pass
    
    # Get required tasks and user progress
    required_tasks = challenge.required_tasks.all()
    user_task_progress = {}
    
    if user_challenge:
        user_tasks = UserTask.objects.filter(
            user=request.user,
            task__in=required_tasks
        ).values('task_id', 'status')
        user_task_progress = {ut['task_id']: ut['status'] for ut in user_tasks}
    
    context = {
        'challenge': challenge,
        'user_challenge': user_challenge,
        'required_tasks': required_tasks,
        'user_task_progress': user_task_progress,
    }
    return render(request, 'eco_tasks/challenge_detail.html', context)
