from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

class User(AbstractUser):
    """Extended User model with gamification features"""
    
    SCHOOL_TYPES = [
        ('elementary', 'Elementary School'),
        ('middle', 'Middle School'),
        ('high', 'High School'),
        ('college', 'College/University'),
    ]
    
    email = models.EmailField(unique=True)
    school_name = models.CharField(max_length=200, blank=True)
    school_type = models.CharField(max_length=20, choices=SCHOOL_TYPES, blank=True)
    grade_level = models.CharField(max_length=50, blank=True)
    bio = models.TextField(max_length=500, blank=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    
    # Gamification fields
    total_eco_tokens = models.PositiveIntegerField(default=0)
    level = models.PositiveIntegerField(default=1)
    experience_points = models.PositiveIntegerField(default=0)
    
    # Location for local leaderboards
    city = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100, blank=True)
    
    # Preferences
    notifications_enabled = models.BooleanField(default=True)
    public_profile = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.username
    
    def get_next_level_xp(self):
        """Calculate XP needed for next level"""
        return self.level * 100
    
    def get_level_progress(self):
        """Get progress percentage to next level"""
        current_level_xp = (self.level - 1) * 100
        next_level_xp = self.level * 100
        progress_xp = self.experience_points - current_level_xp
        total_needed = next_level_xp - current_level_xp
        return (progress_xp / total_needed) * 100 if total_needed > 0 else 0
    
    def add_experience(self, points):
        """Add experience points and handle level ups"""
        self.experience_points += points
        new_level = (self.experience_points // 100) + 1
        if new_level > self.level:
            self.level = new_level
        self.save()
        return new_level > (new_level - 1)  # Return True if leveled up

class UserProfile(models.Model):
    """Additional profile information"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    
    # Achievements
    quizzes_completed = models.PositiveIntegerField(default=0)
    tasks_completed = models.PositiveIntegerField(default=0)
    streak_days = models.PositiveIntegerField(default=0)
    longest_streak = models.PositiveIntegerField(default=0)
    last_activity_date = models.DateField(null=True, blank=True)
    
    # Statistics
    total_quiz_score = models.PositiveIntegerField(default=0)
    average_quiz_score = models.FloatField(default=0.0)
    favorite_topic = models.CharField(max_length=100, blank=True)
    
    def __str__(self):
        return f"{self.user.username}'s Profile"
    
    def update_streak(self):
        """Update daily streak"""
        from datetime import date, timedelta
        
        today = date.today()
        if self.last_activity_date:
            if self.last_activity_date == today - timedelta(days=1):
                self.streak_days += 1
            elif self.last_activity_date != today:
                self.streak_days = 1
        else:
            self.streak_days = 1
            
        if self.streak_days > self.longest_streak:
            self.longest_streak = self.streak_days
            
        self.last_activity_date = today
        self.save()

class Achievement(models.Model):
    """User achievements system"""
    
    ACHIEVEMENT_TYPES = [
        ('quiz', 'Quiz Achievement'),
        ('task', 'Task Achievement'),
        ('streak', 'Streak Achievement'),
        ('social', 'Social Achievement'),
        ('special', 'Special Achievement'),
    ]
    
    name = models.CharField(max_length=100)
    description = models.TextField()
    achievement_type = models.CharField(max_length=20, choices=ACHIEVEMENT_TYPES)
    icon = models.CharField(max_length=50, default='🏆')  # Emoji or icon class
    points_reward = models.PositiveIntegerField(default=0)
    tokens_reward = models.PositiveIntegerField(default=0)
    
    # Criteria
    required_value = models.PositiveIntegerField(default=1)
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name

class UserAchievement(models.Model):
    """Track user achievements"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='achievements')
    achievement = models.ForeignKey(Achievement, on_delete=models.CASCADE)
    earned_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['user', 'achievement']
    
    def __str__(self):
        return f"{self.user.username} - {self.achievement.name}"
