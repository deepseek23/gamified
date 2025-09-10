from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator

User = get_user_model()

class EcoTokenTransaction(models.Model):
    """Track all eco-token transactions"""
    
    TRANSACTION_TYPES = [
        ('earned', 'Tokens Earned'),
        ('spent', 'Tokens Spent'),
        ('bonus', 'Bonus Tokens'),
        ('penalty', 'Penalty'),
        ('gift', 'Gift from User'),
        ('admin', 'Admin Adjustment'),
    ]
    
    EARNING_SOURCES = [
        ('quiz_completion', 'Quiz Completed'),
        ('quiz_perfect', 'Perfect Quiz Score'),
        ('task_completion', 'Eco-Task Completed'),
        ('daily_login', 'Daily Login'),
        ('streak_bonus', 'Streak Bonus'),
        ('level_up', 'Level Up Bonus'),
        ('achievement', 'Achievement Unlocked'),
        ('referral', 'Friend Referral'),
        ('event_participation', 'Event Participation'),
        ('other', 'Other'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='token_transactions')
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES)
    source = models.CharField(max_length=30, choices=EARNING_SOURCES, blank=True)
    amount = models.IntegerField()  # Can be negative for spending
    description = models.CharField(max_length=200)
    
    # Optional references to related objects
    quiz_id = models.PositiveIntegerField(null=True, blank=True)
    task_id = models.PositiveIntegerField(null=True, blank=True)
    achievement_id = models.PositiveIntegerField(null=True, blank=True)
    
    balance_after = models.PositiveIntegerField()  # User's balance after this transaction
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username}: {self.amount} tokens ({self.transaction_type})"

class RewardItem(models.Model):
    """Items that can be purchased with eco-tokens"""
    
    ITEM_TYPES = [
        ('discount', 'Event Discount'),
        ('badge', 'Special Badge'),
        ('avatar', 'Avatar Item'),
        ('certificate', 'Certificate'),
        ('merchandise', 'Eco Merchandise'),
        ('donation', 'Environmental Donation'),
        ('tree_planting', 'Tree Planting'),
        ('other', 'Other Reward'),
    ]
    
    name = models.CharField(max_length=100)
    description = models.TextField()
    item_type = models.CharField(max_length=20, choices=ITEM_TYPES)
    cost_tokens = models.PositiveIntegerField()
    image = models.ImageField(upload_to='rewards/', blank=True, null=True)
    
    # Availability
    is_active = models.BooleanField(default=True)
    stock_quantity = models.PositiveIntegerField(null=True, blank=True)  # None = unlimited
    max_per_user = models.PositiveIntegerField(default=1)
    
    # Requirements
    min_level_required = models.PositiveIntegerField(default=1)
    school_type_restriction = models.CharField(
        max_length=20, 
        choices=User.SCHOOL_TYPES, 
        blank=True,
        help_text="Leave blank for no restriction"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['cost_tokens', 'name']
    
    def __str__(self):
        return f"{self.name} ({self.cost_tokens} tokens)"
    
    def is_available(self):
        """Check if item is available for purchase"""
        if not self.is_active:
            return False
        if self.stock_quantity is not None and self.stock_quantity <= 0:
            return False
        return True
    
    def can_user_purchase(self, user):
        """Check if specific user can purchase this item"""
        if not self.is_available():
            return False, "Item not available"
        
        if user.level < self.min_level_required:
            return False, f"Requires level {self.min_level_required}"
        
        if user.total_eco_tokens < self.cost_tokens:
            return False, "Insufficient tokens"
        
        if self.school_type_restriction and user.school_type != self.school_type_restriction:
            return False, "Not available for your school type"
        
        # Check if user has reached max purchases
        user_purchases = UserReward.objects.filter(user=user, reward_item=self).count()
        if user_purchases >= self.max_per_user:
            return False, f"Maximum {self.max_per_user} per user"
        
        return True, "Available"

class UserReward(models.Model):
    """Track user reward purchases and redemptions"""
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='rewards')
    reward_item = models.ForeignKey(RewardItem, on_delete=models.CASCADE)
    tokens_spent = models.PositiveIntegerField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Delivery/redemption info
    delivery_info = models.JSONField(default=dict, blank=True)  # Address, preferences, etc.
    redemption_code = models.CharField(max_length=50, blank=True)
    notes = models.TextField(blank=True)
    
    purchased_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-purchased_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.reward_item.name}"

class TokenEarningRule(models.Model):
    """Define how many tokens are earned for different activities"""
    
    activity = models.CharField(max_length=30, choices=EcoTokenTransaction.EARNING_SOURCES, unique=True)
    base_tokens = models.PositiveIntegerField()
    bonus_multiplier = models.FloatField(default=1.0, validators=[MinValueValidator(0.1), MaxValueValidator(5.0)])
    
    # Conditions for bonus
    streak_required = models.PositiveIntegerField(default=0, help_text="Days streak required for bonus")
    level_multiplier = models.BooleanField(default=False, help_text="Multiply by user level")
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.get_activity_display()}: {self.base_tokens} tokens"
    
    def calculate_tokens(self, user, streak_days=0):
        """Calculate tokens for a user based on rules"""
        tokens = self.base_tokens
        
        # Apply streak bonus
        if self.streak_required > 0 and streak_days >= self.streak_required:
            tokens = int(tokens * self.bonus_multiplier)
        
        # Apply level multiplier
        if self.level_multiplier:
            tokens = int(tokens * (1 + (user.level - 1) * 0.1))  # 10% per level above 1
        
        return tokens

class DailyTokenLimit(models.Model):
    """Prevent token farming by setting daily limits"""
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField()
    tokens_earned_today = models.PositiveIntegerField(default=0)
    max_daily_tokens = models.PositiveIntegerField(default=100)
    
    class Meta:
        unique_together = ['user', 'date']
    
    def can_earn_tokens(self, amount):
        """Check if user can earn more tokens today"""
        return (self.tokens_earned_today + amount) <= self.max_daily_tokens
    
    def add_tokens(self, amount):
        """Add tokens to daily count"""
        self.tokens_earned_today += amount
        self.save()
