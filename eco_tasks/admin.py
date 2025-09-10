from django.contrib import admin
from .models import (
    TaskCategory, EcoTask, UserTask, TaskSubmissionItem, 
    TaskTemplate, TaskChallenge, UserChallenge
)

@admin.register(TaskCategory)
class TaskCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'icon', 'is_active', 'created_at')
    list_filter = ('is_active',)
    search_fields = ('name', 'description')

@admin.register(EcoTask)
class EcoTaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'difficulty', 'task_type', 'is_active', 'is_featured')
    list_filter = ('category', 'difficulty', 'task_type', 'is_active', 'is_featured', 'verification_method')
    search_fields = ('title', 'description')
    filter_horizontal = ('prerequisite_tasks',)
    list_editable = ('is_active', 'is_featured')
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'description', 'category', 'difficulty', 'task_type', 'image')
        }),
        ('Instructions', {
            'fields': ('instructions', 'materials_needed', 'estimated_time_minutes')
        }),
        ('Verification', {
            'fields': ('verification_method', 'verification_instructions', 'requires_approval')
        }),
        ('Gamification', {
            'fields': ('base_tokens_reward', 'experience_points')
        }),
        ('Requirements', {
            'fields': ('min_level_required', 'prerequisite_tasks')
        }),
        ('Availability', {
            'fields': ('is_active', 'is_featured', 'start_date', 'end_date')
        }),
    )

@admin.register(UserTask)
class UserTaskAdmin(admin.ModelAdmin):
    list_display = ('user', 'task', 'status', 'tokens_earned', 'started_at', 'completed_at')
    list_filter = ('status', 'task__category', 'started_at', 'completed_at')
    search_fields = ('user__username', 'task__title')
    readonly_fields = ('created_at', 'started_at', 'submitted_at', 'completed_at')
    
    fieldsets = (
        ('Task Information', {
            'fields': ('user', 'task', 'status')
        }),
        ('Submission', {
            'fields': ('submission_text', 'submission_image', 'submission_video')
        }),
        ('Tracking', {
            'fields': ('started_at', 'submitted_at', 'completed_at')
        }),
        ('Rewards', {
            'fields': ('tokens_earned', 'experience_gained')
        }),
        ('Review', {
            'fields': ('reviewer_notes', 'reviewed_by', 'reviewed_at')
        }),
    )

@admin.register(TaskSubmissionItem)
class TaskSubmissionItemAdmin(admin.ModelAdmin):
    list_display = ('user_task', 'item_text_preview', 'is_completed', 'created_at')
    list_filter = ('is_completed', 'created_at')
    search_fields = ('user_task__user__username', 'item_text')
    
    def item_text_preview(self, obj):
        return obj.item_text[:50] + "..." if len(obj.item_text) > 50 else obj.item_text
    item_text_preview.short_description = "Item Text"

@admin.register(TaskTemplate)
class TaskTemplateAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'default_tokens', 'default_time_minutes', 'is_active')
    list_filter = ('category', 'is_active')
    search_fields = ('name', 'description')

@admin.register(TaskChallenge)
class TaskChallengeAdmin(admin.ModelAdmin):
    list_display = ('title', 'challenge_type', 'start_date', 'end_date', 'is_active', 'get_participant_count')
    list_filter = ('challenge_type', 'is_active', 'start_date')
    search_fields = ('title', 'description')
    filter_horizontal = ('required_tasks',)
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'description', 'challenge_type')
        }),
        ('Tasks', {
            'fields': ('required_tasks', 'min_tasks_to_complete')
        }),
        ('Timing', {
            'fields': ('start_date', 'end_date')
        }),
        ('Rewards', {
            'fields': ('bonus_tokens', 'bonus_experience', 'badge_name', 'badge_icon')
        }),
        ('Settings', {
            'fields': ('is_active',)
        }),
    )

@admin.register(UserChallenge)
class UserChallengeAdmin(admin.ModelAdmin):
    list_display = ('user', 'challenge', 'status', 'tasks_completed', 'tokens_earned', 'joined_at')
    list_filter = ('status', 'challenge__challenge_type', 'joined_at')
    search_fields = ('user__username', 'challenge__title')
    readonly_fields = ('joined_at', 'completed_at')
