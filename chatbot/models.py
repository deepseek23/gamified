from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()

class ChatSession(models.Model):
    """Chat sessions between users and the eco-learning chatbot"""
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chat_sessions')
    session_id = models.CharField(max_length=100, unique=True)
    
    # Session metadata
    started_at = models.DateTimeField(auto_now_add=True)
    last_activity = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    # Context
    current_topic = models.CharField(max_length=200, blank=True)
    user_intent = models.CharField(max_length=100, blank=True)
    
    def __str__(self):
        return f"{self.user.username} - Session {self.session_id}"

class ChatMessage(models.Model):
    """Individual messages in chat sessions"""
    
    MESSAGE_TYPES = [
        ('user', 'User Message'),
        ('bot', 'Bot Response'),
        ('system', 'System Message'),
    ]
    
    session = models.ForeignKey(ChatSession, on_delete=models.CASCADE, related_name='messages')
    message_type = models.CharField(max_length=10, choices=MESSAGE_TYPES)
    content = models.TextField()
    
    # Metadata
    timestamp = models.DateTimeField(auto_now_add=True)
    response_time_ms = models.PositiveIntegerField(null=True, blank=True)
    
    # Bot response metadata
    confidence_score = models.FloatField(null=True, blank=True)
    intent_detected = models.CharField(max_length=100, blank=True)
    entities_extracted = models.JSONField(default=dict, blank=True)
    
    class Meta:
        ordering = ['timestamp']
    
    def __str__(self):
        return f"{self.session.user.username} - {self.message_type} at {self.timestamp}"

class BotKnowledgeBase(models.Model):
    """Knowledge base for the chatbot responses"""
    
    CONTENT_TYPES = [
        ('faq', 'FAQ'),
        ('quiz_help', 'Quiz Help'),
        ('task_guidance', 'Task Guidance'),
        ('eco_facts', 'Environmental Facts'),
        ('platform_help', 'Platform Help'),
        ('motivation', 'Motivational Content'),
    ]
    
    title = models.CharField(max_length=200)
    content_type = models.CharField(max_length=20, choices=CONTENT_TYPES)
    question = models.TextField()
    answer = models.TextField()
    
    # Keywords for matching
    keywords = models.JSONField(default=list, help_text="Keywords that trigger this response")
    
    # Metadata
    is_active = models.BooleanField(default=True)
    usage_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['content_type', 'title']
    
    def __str__(self):
        return f"{self.title} ({self.get_content_type_display()})"

class ChatbotIntent(models.Model):
    """Define different intents the chatbot can recognize"""
    
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField()
    
    # Training phrases
    training_phrases = models.JSONField(default=list, help_text="Example phrases for this intent")
    
    # Response templates
    response_templates = models.JSONField(default=list, help_text="Template responses for this intent")
    
    # Actions
    requires_context = models.BooleanField(default=False)
    can_trigger_action = models.BooleanField(default=False)
    action_type = models.CharField(max_length=50, blank=True)
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name

class UserFeedback(models.Model):
    """User feedback on chatbot responses"""
    
    FEEDBACK_TYPES = [
        ('helpful', 'Helpful'),
        ('not_helpful', 'Not Helpful'),
        ('incorrect', 'Incorrect Information'),
        ('unclear', 'Unclear Response'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chatbot_feedback')
    message = models.ForeignKey(ChatMessage, on_delete=models.CASCADE, related_name='feedback')
    feedback_type = models.CharField(max_length=20, choices=FEEDBACK_TYPES)
    
    # Optional detailed feedback
    comment = models.TextField(blank=True)
    rating = models.PositiveIntegerField(null=True, blank=True, help_text="1-5 rating")
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.feedback_type}"

class ChatbotAnalytics(models.Model):
    """Analytics for chatbot performance"""
    
    date = models.DateField()
    
    # Usage metrics
    total_sessions = models.PositiveIntegerField(default=0)
    total_messages = models.PositiveIntegerField(default=0)
    unique_users = models.PositiveIntegerField(default=0)
    
    # Performance metrics
    avg_response_time_ms = models.FloatField(default=0.0)
    avg_session_length = models.FloatField(default=0.0)
    
    # Satisfaction metrics
    positive_feedback_count = models.PositiveIntegerField(default=0)
    negative_feedback_count = models.PositiveIntegerField(default=0)
    avg_rating = models.FloatField(default=0.0)
    
    # Popular topics
    top_intents = models.JSONField(default=dict, blank=True)
    
    class Meta:
        unique_together = ['date']
        ordering = ['-date']
    
    def __str__(self):
        return f"Analytics for {self.date}"
