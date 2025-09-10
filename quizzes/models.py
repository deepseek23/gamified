from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
import json

User = get_user_model()

class QuizCategory(models.Model):
    """Categories for organizing quizzes by environmental topics"""
    
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField()
    icon = models.CharField(max_length=50, default='🌱')  # Emoji or icon class
    color = models.CharField(max_length=7, default='#28a745')  # Hex color
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name_plural = "Quiz Categories"
        ordering = ['name']
    
    def __str__(self):
        return self.name

class Quiz(models.Model):
    """Environmental education quizzes"""
    
    DIFFICULTY_LEVELS = [
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
    ]
    
    title = models.CharField(max_length=200)
    description = models.TextField()
    category = models.ForeignKey(QuizCategory, on_delete=models.CASCADE, related_name='quizzes')
    difficulty = models.CharField(max_length=20, choices=DIFFICULTY_LEVELS)
    
    # Gamification
    base_tokens_reward = models.PositiveIntegerField(default=10)
    perfect_score_bonus = models.PositiveIntegerField(default=5)
    time_bonus_enabled = models.BooleanField(default=True)
    max_time_minutes = models.PositiveIntegerField(default=10)
    
    # Requirements
    min_level_required = models.PositiveIntegerField(default=1)
    prerequisite_quizzes = models.ManyToManyField('self', blank=True, symmetrical=False)
    
    # Settings
    is_active = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    randomize_questions = models.BooleanField(default=True)
    show_correct_answers = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['category', 'difficulty', 'title']
    
    def __str__(self):
        return f"{self.title} ({self.get_difficulty_display()})"
    
    def get_questions_count(self):
        return self.questions.count()
    
    def get_average_score(self):
        attempts = QuizAttempt.objects.filter(quiz=self, is_completed=True)
        if attempts.exists():
            return attempts.aggregate(models.Avg('score'))['score__avg']
        return 0
    
    def get_completion_rate(self):
        total_attempts = QuizAttempt.objects.filter(quiz=self).count()
        completed_attempts = QuizAttempt.objects.filter(quiz=self, is_completed=True).count()
        if total_attempts > 0:
            return (completed_attempts / total_attempts) * 100
        return 0

class Question(models.Model):
    """Quiz questions with multiple choice answers"""
    
    QUESTION_TYPES = [
        ('multiple_choice', 'Multiple Choice'),
        ('true_false', 'True/False'),
        ('fill_blank', 'Fill in the Blank'),
    ]
    
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='questions')
    question_type = models.CharField(max_length=20, choices=QUESTION_TYPES, default='multiple_choice')
    text = models.TextField()
    explanation = models.TextField(blank=True, help_text="Explanation shown after answering")
    
    # Media
    image = models.ImageField(upload_to='quiz_images/', blank=True, null=True)
    
    # Scoring
    points = models.PositiveIntegerField(default=1)
    order = models.PositiveIntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['quiz', 'order']
    
    def __str__(self):
        return f"{self.quiz.title} - Q{self.order}"
    
    def get_correct_answer(self):
        return self.answers.filter(is_correct=True).first()

class Answer(models.Model):
    """Answer choices for questions"""
    
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='answers')
    text = models.CharField(max_length=500)
    is_correct = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0)
    
    class Meta:
        ordering = ['question', 'order']
    
    def __str__(self):
        return f"{self.question} - {self.text[:50]}"

class QuizAttempt(models.Model):
    """Track user quiz attempts and scores"""
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='quiz_attempts')
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='attempts')
    
    # Attempt details
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    is_completed = models.BooleanField(default=False)
    
    # Scoring
    score = models.FloatField(default=0.0, validators=[MinValueValidator(0.0), MaxValueValidator(100.0)])
    total_questions = models.PositiveIntegerField(default=0)
    correct_answers = models.PositiveIntegerField(default=0)
    
    # Gamification
    tokens_earned = models.PositiveIntegerField(default=0)
    experience_gained = models.PositiveIntegerField(default=0)
    time_taken_seconds = models.PositiveIntegerField(default=0)
    
    # Data
    answers_data = models.JSONField(default=dict)  # Store user's answers
    
    class Meta:
        ordering = ['-started_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.quiz.title} ({self.score}%)"
    
    def calculate_score(self):
        """Calculate the final score based on correct answers"""
        if self.total_questions > 0:
            self.score = (self.correct_answers / self.total_questions) * 100
        else:
            self.score = 0
        return self.score
    
    def is_perfect_score(self):
        return self.score == 100.0
    
    def get_time_bonus_tokens(self):
        """Calculate time bonus tokens if applicable"""
        if not self.quiz.time_bonus_enabled or self.time_taken_seconds == 0:
            return 0
        
        max_time_seconds = self.quiz.max_time_minutes * 60
        if self.time_taken_seconds < max_time_seconds * 0.5:  # Completed in less than half the time
            return 3
        elif self.time_taken_seconds < max_time_seconds * 0.75:  # Completed in less than 3/4 time
            return 2
        return 0

class UserAnswer(models.Model):
    """Individual answers given by users"""
    
    attempt = models.ForeignKey(QuizAttempt, on_delete=models.CASCADE, related_name='user_answers')
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    selected_answer = models.ForeignKey(Answer, on_delete=models.CASCADE, null=True, blank=True)
    text_answer = models.TextField(blank=True)  # For fill-in-the-blank questions
    is_correct = models.BooleanField(default=False)
    answered_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['attempt', 'question']
    
    def __str__(self):
        return f"{self.attempt.user.username} - {self.question}"

class QuizLeaderboard(models.Model):
    """Leaderboard entries for quizzes"""
    
    LEADERBOARD_TYPES = [
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
        ('all_time', 'All Time'),
    ]
    
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='leaderboard_entries')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    leaderboard_type = models.CharField(max_length=20, choices=LEADERBOARD_TYPES)
    
    best_score = models.FloatField()
    best_time_seconds = models.PositiveIntegerField()
    total_attempts = models.PositiveIntegerField(default=1)
    rank = models.PositiveIntegerField()
    
    period_start = models.DateTimeField()
    period_end = models.DateTimeField()
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['quiz', 'user', 'leaderboard_type', 'period_start']
        ordering = ['quiz', 'leaderboard_type', 'rank']
    
    def __str__(self):
        return f"{self.quiz.title} - {self.user.username} (#{self.rank})"
