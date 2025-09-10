from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.generic import DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from .forms import CustomUserCreationForm, UserProfileForm
from .models import User, UserProfile, UserAchievement

def register(request):
    """User registration view"""
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Create user profile
            UserProfile.objects.create(user=user)
            login(request, user)
            messages.success(request, 'Welcome to EcoLearning! Your journey starts now!')
            return redirect('home')
    else:
        form = CustomUserCreationForm()
    return render(request, 'accounts/register.html', {'form': form})

@login_required
def profile_view(request):
    """User profile view"""
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    achievements = UserAchievement.objects.filter(user=request.user).select_related('achievement')
    
    context = {
        'user': request.user,
        'profile': profile,
        'achievements': achievements,
        'level_progress': request.user.get_level_progress(),
        'next_level_xp': request.user.get_next_level_xp(),
    }
    return render(request, 'accounts/profile.html', context)

@login_required
def edit_profile(request):
    """Edit user profile"""
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('accounts:profile')
    else:
        form = UserProfileForm(instance=request.user)
    return render(request, 'accounts/edit_profile.html', {'form': form})

class PublicProfileView(DetailView):
    """Public profile view for other users"""
    model = User
    template_name = 'accounts/public_profile.html'
    context_object_name = 'profile_user'
    slug_field = 'username'
    slug_url_kwarg = 'username'
    
    def get_queryset(self):
        return User.objects.filter(public_profile=True)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.get_object()
        profile, created = UserProfile.objects.get_or_create(user=user)
        achievements = UserAchievement.objects.filter(user=user).select_related('achievement')
        
        context.update({
            'profile': profile,
            'achievements': achievements,
            'level_progress': user.get_level_progress(),
        })
        return context

@login_required
def dashboard(request):
    """User dashboard with overview"""
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    recent_achievements = UserAchievement.objects.filter(
        user=request.user
    ).select_related('achievement').order_by('-earned_at')[:5]
    
    context = {
        'user': request.user,
        'profile': profile,
        'recent_achievements': recent_achievements,
        'level_progress': request.user.get_level_progress(),
    }
    return render(request, 'accounts/dashboard.html', context)
