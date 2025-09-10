from django.contrib import admin
from .models import QuizCategory, Quiz, Question, Answer, QuizAttempt, UserAnswer, QuizLeaderboard

class AnswerInline(admin.TabularInline):
    model = Answer
    extra = 4
    fields = ('text', 'is_correct', 'order')

@admin.register(QuizCategory)
class QuizCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'icon', 'is_active', 'created_at')
    list_filter = ('is_active',)
    search_fields = ('name', 'description')

@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'difficulty', 'is_active', 'is_featured', 'get_questions_count')
    list_filter = ('category', 'difficulty', 'is_active', 'is_featured')
    search_fields = ('title', 'description')
    filter_horizontal = ('prerequisite_quizzes',)
    list_editable = ('is_active', 'is_featured')

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('quiz', 'question_type', 'text_preview', 'points', 'order')
    list_filter = ('question_type', 'quiz__category')
    search_fields = ('text', 'quiz__title')
    inlines = [AnswerInline]
    
    def text_preview(self, obj):
        return obj.text[:100] + "..." if len(obj.text) > 100 else obj.text
    text_preview.short_description = "Question Text"

@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = ('question', 'text_preview', 'is_correct', 'order')
    list_filter = ('is_correct', 'question__quiz__category')
    search_fields = ('text', 'question__text')
    
    def text_preview(self, obj):
        return obj.text[:50] + "..." if len(obj.text) > 50 else obj.text
    text_preview.short_description = "Answer Text"

@admin.register(QuizAttempt)
class QuizAttemptAdmin(admin.ModelAdmin):
    list_display = ('user', 'quiz', 'score', 'is_completed', 'tokens_earned', 'started_at')
    list_filter = ('is_completed', 'quiz__category', 'started_at')
    search_fields = ('user__username', 'quiz__title')
    readonly_fields = ('started_at', 'completed_at')

@admin.register(UserAnswer)
class UserAnswerAdmin(admin.ModelAdmin):
    list_display = ('attempt', 'question', 'selected_answer', 'is_correct', 'answered_at')
    list_filter = ('is_correct', 'answered_at')
    search_fields = ('attempt__user__username', 'question__text')

@admin.register(QuizLeaderboard)
class QuizLeaderboardAdmin(admin.ModelAdmin):
    list_display = ('quiz', 'user', 'leaderboard_type', 'best_score', 'rank', 'updated_at')
    list_filter = ('leaderboard_type', 'quiz__category', 'updated_at')
    search_fields = ('user__username', 'quiz__title')
