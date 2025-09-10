from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from datetime import timedelta

User = get_user_model()

class TaskCategory(models.Model):
    """Categories for organizing eco-tasks"""
    
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField()
    icon = models.CharField(max_length=50, default='🌍')  # Emoji or icon class
    color = models.CharField(max_length=7, default='#28a745')  # Hex color
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name_plural = "Task Categories"
        ordering = ['name']
    
    def __str__(self):
        return self.name

class EcoTask(models.Model):
    """Real-world environmental tasks for students"""
    
    DIFFICULTY_LEVELS = [
        ('easy', 'Easy'),
        ('medium', 'Medium'),
        ('hard', 'Hard'),
    ]
    
    TASK_TYPES = [
        ('individual', 'Individual Task'),
        ('group', 'Group Task'),
        ('family', 'Family Task'),
        ('school', 'School-wide Task'),
        ('community', 'Community Task'),
    ]
    
    VERIFICATION_METHODS = [
        ('photo', 'Photo Upload'),
        ('video', 'Video Upload'),
        ('text', 'Text Description'),
        ('checklist', 'Checklist'),
        ('quiz', 'Mini Quiz'),
        ('peer_review', 'Peer Review'),
    ]
    
    title = models.CharField(max_length=200)
    description = models.TextField()
    category = models.ForeignKey(TaskCategory, on_delete=models.CASCADE, related_name='tasks')
    difficulty = models.CharField(max_length=20, choices=DIFFICULTY_LEVELS)
    task_type = models.CharField(max_length=20, choices=TASK_TYPES)
    
    # Instructions and requirements
    instructions = models.TextField()
    materials_needed = models.TextField(blank=True)
    estimated_time_minutes = models.PositiveIntegerField()
    
    # Verification
    verification_method = models.CharField(max_length=20, choices=VERIFICATION_METHODS)
    verification_instructions = models.TextField()
    requires_approval = models.BooleanField(default=True)
    
    # Gamification
    base_tokens_reward = models.PositiveIntegerField(default=15)
    experience_points = models.PositiveIntegerField(default=10)
    
    # Requirements
    min_level_required = models.PositiveIntegerField(default=1)
    prerequisite_tasks = models.ManyToManyField('self', blank=True, symmetrical=False)
    
    # Availability
    is_active = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    start_date = models.DateTimeField(null=True, blank=True)
    end_date = models.DateTimeField(null=True, blank=True)
    
    # Media
    image = models.ImageField(upload_to='task_images/', blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['category', 'difficulty', 'title']
    
    def __str__(self):
        return f"{self.title} ({self.get_difficulty_display()})"
    
    def is_available(self):
        """Check if task is currently available"""
        if not self.is_active:
            return False
        
        now = timezone.now()
        if self.start_date and now < self.start_date:
            return False
        if self.end_date and now > self.end_date:
            return False
        
        return True
    
    def get_completion_count(self):
        return UserTask.objects.filter(task=self, status='completed').count()
    
    def get_completion_rate(self):
        total_attempts = UserTask.objects.filter(task=self).count()
        completed = self.get_completion_count()
        if total_attempts > 0:
            return (completed / total_attempts) * 100
        return 0

class UserTask(models.Model):
    """Track user task attempts and completions"""
    
    STATUS_CHOICES = [
        ('not_started', 'Not Started'),
        ('in_progress', 'In Progress'),
        ('submitted', 'Submitted for Review'),
        ('completed', 'Completed'),
        ('rejected', 'Rejected'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='eco_tasks')
    task = models.ForeignKey(EcoTask, on_delete=models.CASCADE, related_name='user_attempts')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='not_started')
    
    # Submission data
    submission_text = models.TextField(blank=True)
    submission_image = models.ImageField(upload_to='task_submissions/', blank=True, null=True)
    submission_video = models.FileField(upload_to='task_videos/', blank=True, null=True)
    
    # Tracking
    started_at = models.DateTimeField(null=True, blank=True)
    submitted_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    # Rewards
    tokens_earned = models.PositiveIntegerField(default=0)
    experience_gained = models.PositiveIntegerField(default=0)
    
    # Review
    reviewer_notes = models.TextField(blank=True)
    reviewed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='reviewed_tasks')
    reviewed_at = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['user', 'task']
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.task.title} ({self.status})"
    
    def can_start(self):
        """Check if user can start this task"""
        if self.status != 'not_started':
            return False, "Task already started"
        
        if not self.task.is_available():
            return False, "Task not available"
        
        if self.user.level < self.task.min_level_required:
            return False, f"Requires level {self.task.min_level_required}"
        
        return True, "Can start"
    
    def start_task(self):
        """Start the task"""
        can_start, message = self.can_start()
        if can_start:
            self.status = 'in_progress'
            self.started_at = timezone.now()
            self.save()
            return True
        return False

class TaskSubmissionItem(models.Model):
    """Individual items in a task submission (for checklist-type tasks)"""
    
    user_task = models.ForeignKey(UserTask, on_delete=models.CASCADE, related_name='submission_items')
    item_text = models.CharField(max_length=500)
    is_completed = models.BooleanField(default=False)
    notes = models.TextField(blank=True)
    image = models.ImageField(upload_to='task_item_images/', blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user_task} - {self.item_text[:50]}"

class TaskTemplate(models.Model):
    """Templates for creating common task types"""
    
    name = models.CharField(max_length=100)
    description = models.TextField()
    category = models.ForeignKey(TaskCategory, on_delete=models.CASCADE)
    
    # Template fields
    template_instructions = models.TextField()
    template_materials = models.TextField(blank=True)
    template_verification = models.TextField()
    
    default_tokens = models.PositiveIntegerField(default=15)
    default_experience = models.PositiveIntegerField(default=10)
    default_time_minutes = models.PositiveIntegerField(default=30)
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name

class TaskChallenge(models.Model):
    """Special challenges involving multiple tasks"""
    
    CHALLENGE_TYPES = [
        ('weekly', 'Weekly Challenge'),
        ('monthly', 'Monthly Challenge'),
        ('seasonal', 'Seasonal Challenge'),
        ('special', 'Special Event'),
    ]
    
    title = models.CharField(max_length=200)
    description = models.TextField()
    challenge_type = models.CharField(max_length=20, choices=CHALLENGE_TYPES)
    
    # Tasks involved
    required_tasks = models.ManyToManyField(EcoTask, related_name='challenges')
    min_tasks_to_complete = models.PositiveIntegerField(default=1)
    
    # Timing
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    
    # Rewards
    bonus_tokens = models.PositiveIntegerField(default=50)
    bonus_experience = models.PositiveIntegerField(default=25)
    
    # Badge/Achievement
    badge_name = models.CharField(max_length=100, blank=True)
    badge_icon = models.CharField(max_length=50, default='🏆')
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-start_date']
    
    def __str__(self):
        return self.title
    
    def is_available(self):
        """Check if challenge is currently active"""
        if not self.is_active:
            return False
        
        now = timezone.now()
        return self.start_date <= now <= self.end_date
    
    def get_participant_count(self):
        return UserChallenge.objects.filter(challenge=self).count()

class UserChallenge(models.Model):
    """Track user participation in challenges"""
    
    STATUS_CHOICES = [
        ('joined', 'Joined'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='challenges')
    challenge = models.ForeignKey(TaskChallenge, on_delete=models.CASCADE, related_name='participants')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='joined')
    
    # Progress tracking
    tasks_completed = models.PositiveIntegerField(default=0)
    joined_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    # Rewards
    tokens_earned = models.PositiveIntegerField(default=0)
    experience_gained = models.PositiveIntegerField(default=0)
    
    class Meta:
        unique_together = ['user', 'challenge']
    
    def __str__(self):
        return f"{self.user.username} - {self.challenge.title}"
    
    def check_completion(self):
        """Check if user has completed the challenge"""
        if self.tasks_completed >= self.challenge.min_tasks_to_complete:
            if self.status != 'completed':
                self.status = 'completed'
                self.completed_at = timezone.now()
                self.tokens_earned = self.challenge.bonus_tokens
                self.experience_gained = self.challenge.bonus_experience
                self.save()
                return True
        return False
