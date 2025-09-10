from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import datetime, timedelta

User = get_user_model()

class LeaderboardType(models.Model):
    """Different types of leaderboards"""
    
    SCOPE_CHOICES = [
        ('global', 'Global'),
        ('country', 'Country'),
        ('city', 'City'),
        ('school', 'School'),
        ('grade', 'Grade Level'),
    ]
    
    PERIOD_CHOICES = [
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
        ('yearly', 'Yearly'),
        ('all_time', 'All Time'),
    ]
    
    METRIC_CHOICES = [
        ('total_tokens', 'Total Eco-Tokens'),
        ('level', 'User Level'),
        ('quiz_score', 'Average Quiz Score'),
        ('tasks_completed', 'Tasks Completed'),
        ('streak_days', 'Current Streak'),
        ('longest_streak', 'Longest Streak'),
        ('quizzes_completed', 'Quizzes Completed'),
    ]
    
    name = models.CharField(max_length=100)
    description = models.TextField()
    scope = models.CharField(max_length=20, choices=SCOPE_CHOICES)
    period = models.CharField(max_length=20, choices=PERIOD_CHOICES)
    metric = models.CharField(max_length=30, choices=METRIC_CHOICES)
    
    # Display settings
    icon = models.CharField(max_length=50, default='🏆')
    color = models.CharField(max_length=7, default='#ffd700')
    max_entries = models.PositiveIntegerField(default=100)
    
    # Filters
    school_type_filter = models.CharField(
        max_length=20, 
        choices=User.SCHOOL_TYPES, 
        blank=True,
        help_text="Leave blank for no filter"
    )
    min_level = models.PositiveIntegerField(default=1)
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['scope', 'period', 'metric']
    
    def __str__(self):
        return f"{self.name} ({self.get_scope_display()} - {self.get_period_display()})"

class LeaderboardEntry(models.Model):
    """Individual entries in leaderboards"""
    
    leaderboard_type = models.ForeignKey(LeaderboardType, on_delete=models.CASCADE, related_name='entries')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='leaderboard_entries')
    
    # Position and score
    rank = models.PositiveIntegerField()
    score = models.FloatField()
    previous_rank = models.PositiveIntegerField(null=True, blank=True)
    
    # Period information
    period_start = models.DateTimeField()
    period_end = models.DateTimeField()
    
    # Additional data
    additional_data = models.JSONField(default=dict, blank=True)  # Store extra metrics
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['leaderboard_type', 'user', 'period_start']
        ordering = ['leaderboard_type', 'rank']
    
    def __str__(self):
        return f"{self.leaderboard_type.name} - #{self.rank} {self.user.username}"
    
    def get_rank_change(self):
        """Get rank change from previous period"""
        if self.previous_rank:
            return self.previous_rank - self.rank
        return 0
    
    def get_rank_change_display(self):
        """Get formatted rank change"""
        change = self.get_rank_change()
        if change > 0:
            return f"↑{change}"
        elif change < 0:
            return f"↓{abs(change)}"
        return "="

class GlobalLeaderboard(models.Model):
    """Global leaderboard aggregating all users"""
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='global_rankings')
    
    # Overall rankings
    global_rank = models.PositiveIntegerField()
    total_score = models.FloatField()  # Composite score
    
    # Individual metrics
    tokens_rank = models.PositiveIntegerField(null=True, blank=True)
    level_rank = models.PositiveIntegerField(null=True, blank=True)
    quiz_rank = models.PositiveIntegerField(null=True, blank=True)
    task_rank = models.PositiveIntegerField(null=True, blank=True)
    
    # Badges and achievements
    total_achievements = models.PositiveIntegerField(default=0)
    rare_achievements = models.PositiveIntegerField(default=0)
    
    last_updated = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['global_rank']
    
    def __str__(self):
        return f"Global #{self.global_rank} - {self.user.username}"

class LocalLeaderboard(models.Model):
    """Local leaderboards by geographic location"""
    
    LOCATION_TYPES = [
        ('country', 'Country'),
        ('city', 'City'),
        ('school', 'School'),
    ]
    
    location_type = models.CharField(max_length=20, choices=LOCATION_TYPES)
    location_value = models.CharField(max_length=200)  # Country name, city name, etc.
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='local_rankings')
    rank = models.PositiveIntegerField()
    score = models.FloatField()
    
    # Period
    period_type = models.CharField(max_length=20, choices=LeaderboardType.PERIOD_CHOICES)
    period_start = models.DateTimeField()
    period_end = models.DateTimeField()
    
    last_updated = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['location_type', 'location_value', 'user', 'period_type', 'period_start']
        ordering = ['location_type', 'location_value', 'rank']
    
    def __str__(self):
        return f"{self.location_value} #{self.rank} - {self.user.username}"

class LeaderboardReward(models.Model):
    """Rewards for leaderboard positions"""
    
    leaderboard_type = models.ForeignKey(LeaderboardType, on_delete=models.CASCADE, related_name='rewards')
    
    # Position criteria
    min_rank = models.PositiveIntegerField(default=1)
    max_rank = models.PositiveIntegerField(default=1)
    
    # Rewards
    token_reward = models.PositiveIntegerField(default=0)
    experience_reward = models.PositiveIntegerField(default=0)
    badge_name = models.CharField(max_length=100, blank=True)
    badge_icon = models.CharField(max_length=50, blank=True)
    
    # Special rewards
    special_title = models.CharField(max_length=100, blank=True)
    custom_avatar_frame = models.CharField(max_length=100, blank=True)
    
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        if self.min_rank == self.max_rank:
            return f"{self.leaderboard_type.name} - Rank #{self.min_rank}"
        return f"{self.leaderboard_type.name} - Ranks #{self.min_rank}-{self.max_rank}"

class UserLeaderboardReward(models.Model):
    """Track rewards given to users for leaderboard positions"""
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='leaderboard_rewards')
    leaderboard_reward = models.ForeignKey(LeaderboardReward, on_delete=models.CASCADE)
    leaderboard_entry = models.ForeignKey(LeaderboardEntry, on_delete=models.CASCADE)
    
    tokens_awarded = models.PositiveIntegerField()
    experience_awarded = models.PositiveIntegerField()
    
    awarded_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['user', 'leaderboard_reward', 'leaderboard_entry']
    
    def __str__(self):
        return f"{self.user.username} - {self.leaderboard_reward}"

class LeaderboardSeason(models.Model):
    """Seasonal competitions with special themes"""
    
    SEASON_TYPES = [
        ('spring', 'Spring Challenge'),
        ('summer', 'Summer Challenge'),
        ('fall', 'Fall Challenge'),
        ('winter', 'Winter Challenge'),
        ('earth_day', 'Earth Day Special'),
        ('environment_week', 'Environment Week'),
        ('custom', 'Custom Event'),
    ]
    
    name = models.CharField(max_length=100)
    description = models.TextField()
    season_type = models.CharField(max_length=20, choices=SEASON_TYPES)
    
    # Timing
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    
    # Special rules
    bonus_multiplier = models.FloatField(default=1.0)
    featured_activities = models.JSONField(default=list, blank=True)  # List of activity types
    
    # Rewards
    winner_tokens = models.PositiveIntegerField(default=500)
    winner_badge = models.CharField(max_length=100, blank=True)
    participation_tokens = models.PositiveIntegerField(default=50)
    
    # Display
    theme_color = models.CharField(max_length=7, default='#28a745')
    banner_image = models.ImageField(upload_to='season_banners/', blank=True, null=True)
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-start_date']
    
    def __str__(self):
        return self.name
    
    def is_running(self):
        """Check if season is currently active"""
        now = timezone.now()
        return self.is_active and self.start_date <= now <= self.end_date
    
    def get_participants_count(self):
        """Get number of participants in this season"""
        return SeasonParticipant.objects.filter(season=self).count()

class SeasonParticipant(models.Model):
    """Track user participation in seasonal competitions"""
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='season_participations')
    season = models.ForeignKey(LeaderboardSeason, on_delete=models.CASCADE, related_name='participants')
    
    # Performance
    season_score = models.FloatField(default=0.0)
    season_rank = models.PositiveIntegerField(null=True, blank=True)
    
    # Activities during season
    quizzes_completed = models.PositiveIntegerField(default=0)
    tasks_completed = models.PositiveIntegerField(default=0)
    tokens_earned = models.PositiveIntegerField(default=0)
    
    # Rewards
    rewards_claimed = models.BooleanField(default=False)
    final_tokens_awarded = models.PositiveIntegerField(default=0)
    
    joined_at = models.DateTimeField(auto_now_add=True)
    last_activity = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['user', 'season']
        ordering = ['season', 'season_rank']
    
    def __str__(self):
        return f"{self.user.username} - {self.season.name}"
