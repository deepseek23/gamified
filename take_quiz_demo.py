#!/usr/bin/env python
import os
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'eco_learning_platform.settings')
django.setup()

from django.contrib.auth import get_user_model
from quizzes.models import Quiz, QuizAttempt, UserAnswer, Question, Answer
from django.utils import timezone

User = get_user_model()

# Get the test student
student = User.objects.get(username='testuser')
print(f"🎓 Student: {student.username}")
print(f"💰 Current Tokens: {student.total_eco_tokens}")
print(f"⭐ Level: {student.level}")
print()

# Get available quiz
quiz = Quiz.objects.filter(title="Sustainable Living Challenge").first()
print(f"📚 Taking Quiz: {quiz.title}")
print(f"🎯 Difficulty: {quiz.get_difficulty_display()}")
print(f"💰 Reward: {quiz.base_tokens_reward} + {quiz.perfect_score_bonus} bonus tokens")
print()

# Create quiz attempt
attempt = QuizAttempt.objects.create(
    user=student,
    quiz=quiz,
    total_questions=quiz.get_questions_count()
)

# Get questions
questions = list(quiz.questions.all().order_by('order'))
correct_count = 0

print("📝 QUIZ QUESTIONS:")
print("=" * 60)

# Answer each question
for i, question in enumerate(questions, 1):
    print(f"Question {i}: {question.text}")
    
    answers = list(question.answers.all().order_by('order'))
    for j, answer in enumerate(answers, 1):
        print(f"  {j}. {answer.text}")
    
    # Select correct answer (simulate perfect score)
    correct_answer = next(a for a in answers if a.is_correct)
    
    UserAnswer.objects.create(
        attempt=attempt,
        question=question,
        selected_answer=correct_answer,
        is_correct=True
    )
    
    correct_count += 1
    print(f"  ✅ Selected: {correct_answer.text}")
    print(f"  💡 Explanation: {question.explanation}")
    print()

# Complete quiz
attempt.correct_answers = correct_count
attempt.calculate_score()
attempt.is_completed = True
attempt.completed_at = timezone.now()
attempt.time_taken_seconds = 480  # 8 minutes
attempt.tokens_earned = quiz.base_tokens_reward + quiz.perfect_score_bonus
attempt.experience_gained = attempt.tokens_earned
attempt.save()

# Update student
student.total_eco_tokens += attempt.tokens_earned
student.experience_points += attempt.experience_gained
student.save()

print("🎉 QUIZ COMPLETED!")
print("=" * 60)
print(f"📊 Final Score: {attempt.score}%")
print(f"✅ Correct: {correct_count}/{len(questions)}")
print(f"⏱️  Time: 8 minutes")
print(f"💰 Tokens Earned: {attempt.tokens_earned}")
print(f"⭐ Experience: {attempt.experience_gained}")
print()
print(f"👤 Updated Student Stats:")
print(f"   💰 Total Tokens: {student.total_eco_tokens}")
print(f"   ⭐ Experience: {student.experience_points}")
print(f"   🏆 Level: {student.level}")
print()
print(f"🌐 View on website: http://localhost:8000/quizzes/complete/{attempt.id}/")
