from django.contrib import admin
from .models import (
    ChatSession, ChatMessage, BotKnowledgeBase, 
    ChatbotIntent, UserFeedback, ChatbotAnalytics
)

@admin.register(ChatSession)
class ChatSessionAdmin(admin.ModelAdmin):
    list_display = ('user', 'session_id', 'current_topic', 'is_active', 'started_at', 'last_activity')
    list_filter = ('is_active', 'started_at', 'current_topic')
    search_fields = ('user__username', 'session_id', 'current_topic')
    readonly_fields = ('started_at', 'last_activity')

@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ('session', 'message_type', 'content_preview', 'timestamp', 'confidence_score')
    list_filter = ('message_type', 'timestamp')
    search_fields = ('session__user__username', 'content', 'intent_detected')
    readonly_fields = ('timestamp',)
    
    def content_preview(self, obj):
        return obj.content[:100] + "..." if len(obj.content) > 100 else obj.content
    content_preview.short_description = "Content"

@admin.register(BotKnowledgeBase)
class BotKnowledgeBaseAdmin(admin.ModelAdmin):
    list_display = ('title', 'content_type', 'is_active', 'usage_count', 'updated_at')
    list_filter = ('content_type', 'is_active', 'created_at')
    search_fields = ('title', 'question', 'answer')
    list_editable = ('is_active',)

@admin.register(ChatbotIntent)
class ChatbotIntentAdmin(admin.ModelAdmin):
    list_display = ('name', 'requires_context', 'can_trigger_action', 'is_active', 'created_at')
    list_filter = ('requires_context', 'can_trigger_action', 'is_active')
    search_fields = ('name', 'description')

@admin.register(UserFeedback)
class UserFeedbackAdmin(admin.ModelAdmin):
    list_display = ('user', 'feedback_type', 'rating', 'created_at')
    list_filter = ('feedback_type', 'rating', 'created_at')
    search_fields = ('user__username', 'comment')

@admin.register(ChatbotAnalytics)
class ChatbotAnalyticsAdmin(admin.ModelAdmin):
    list_display = ('date', 'total_sessions', 'unique_users', 'avg_response_time_ms', 'avg_rating')
    list_filter = ('date',)
    readonly_fields = ('date',)
