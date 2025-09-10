from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, UserProfile, Achievement, UserAchievement

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'school_name', 'level', 'total_eco_tokens', 'is_staff')
    list_filter = ('school_type', 'level', 'is_staff', 'is_active', 'date_joined')
    search_fields = ('username', 'email', 'school_name')
    
    fieldsets = UserAdmin.fieldsets + (
        ('School Information', {
            'fields': ('school_name', 'school_type', 'grade_level')
        }),
        ('Profile', {
            'fields': ('bio', 'avatar', 'city', 'country')
        }),
        ('Gamification', {
            'fields': ('total_eco_tokens', 'level', 'experience_points')
        }),
        ('Preferences', {
            'fields': ('notifications_enabled', 'public_profile')
        }),
    )

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'quizzes_completed', 'tasks_completed', 'streak_days', 'average_quiz_score')
    list_filter = ('streak_days', 'favorite_topic')
    search_fields = ('user__username', 'user__email')

@admin.register(Achievement)
class AchievementAdmin(admin.ModelAdmin):
    list_display = ('name', 'achievement_type', 'points_reward', 'tokens_reward', 'is_active')
    list_filter = ('achievement_type', 'is_active')
    search_fields = ('name', 'description')

@admin.register(UserAchievement)
class UserAchievementAdmin(admin.ModelAdmin):
    list_display = ('user', 'achievement', 'earned_at')
    list_filter = ('achievement__achievement_type', 'earned_at')
    search_fields = ('user__username', 'achievement__name')
