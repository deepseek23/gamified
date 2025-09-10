#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'eco_learning_platform.settings')
django.setup()

from django.contrib.auth import get_user_model
from quizzes.models import Quiz, QuizAttempt, UserAnswer
from django.utils import timezone

User = get_user_model()

def demo_student_quiz():
    # Get student
    student = User.objects.get(username='testuser')
    quiz = Quiz.objects.filter(title='Sustainable Living Challenge').first()
    
    print("🎓 STUDENT QUIZ DEMONSTRATION")
    print("=" * 60)
    print(f"👤 Student: {student.username} (Level {student.level})")
    print(f"💰 Current Tokens: {student.total_eco_tokens}")
    print(f"📚 Quiz: {quiz.title}")
    print(f"🎯 Difficulty: {quiz.get_difficulty_display()}")
    print(f"💎 Rewards: {quiz.base_tokens_reward} base + {quiz.perfect_score_bonus} bonus tokens")
    print(f"⏱️  Time Limit: {quiz.max_time_minutes} minutes")
    print()
    
    # Create quiz attempt
    attempt = QuizAttempt.objects.create(
        user=student,
        quiz=quiz,
        total_questions=quiz.get_questions_count()
    )
    
    print("📝 TAKING QUIZ - QUESTIONS & ANSWERS:")
    print("=" * 60)
    
    # Get questions
    questions = list(quiz.questions.all().order_by('order'))
    correct_count = 0
    
    for i, question in enumerate(questions, 1):
        print(f"\n🔸 Question {i}/{len(questions)}: {question.text}")
        
        # Show answer options
        answers = list(question.answers.all().order_by('order'))
        for j, answer in enumerate(answers, 1):
            marker = "✓" if answer.is_correct else " "
            print(f"   [{marker}] {chr(64+j)}. {answer.text}")
        
        # Student selects correct answer (perfect score simulation)
        correct_answer = next(a for a in answers if a.is_correct)
        
        # Record answer
        UserAnswer.objects.create(
            attempt=attempt,
            question=question,
            selected_answer=correct_answer,
            is_correct=True
        )
        
        correct_count += 1
        print(f"   ✅ Student Selected: {correct_answer.text}")
        print(f"   💡 Explanation: {question.explanation}")
    
    # Complete the quiz
    attempt.correct_answers = correct_count
    attempt.calculate_score()
    attempt.is_completed = True
    attempt.completed_at = timezone.now()
    attempt.time_taken_seconds = 480  # 8 minutes
    
    # Calculate rewards
    total_tokens = quiz.base_tokens_reward + quiz.perfect_score_bonus  # Perfect score
    attempt.tokens_earned = total_tokens
    attempt.experience_gained = total_tokens
    attempt.save()
    
    # Update student stats
    old_tokens = student.total_eco_tokens
    student.total_eco_tokens += total_tokens
    student.experience_points += total_tokens
    student.save()
    
    print("\n" + "=" * 60)
    print("🎉 QUIZ COMPLETED - RESULTS")
    print("=" * 60)
    print(f"📊 Final Score: {attempt.score}% (Perfect Score!)")
    print(f"✅ Correct Answers: {correct_count}/{len(questions)}")
    print(f"⏱️  Time Taken: 8 minutes")
    print(f"💰 Tokens Earned: {total_tokens}")
    print(f"   • Base Reward: {quiz.base_tokens_reward}")
    print(f"   • Perfect Bonus: {quiz.perfect_score_bonus}")
    print(f"⭐ Experience Gained: {total_tokens}")
    print()
    print("👤 UPDATED STUDENT PROFILE:")
    print(f"   💰 Tokens: {old_tokens} → {student.total_eco_tokens} (+{total_tokens})")
    print(f"   ⭐ Experience: {student.experience_points}")
    print(f"   🏆 Level: {student.level}")
    print()
    print(f"🌐 View Results Online: http://localhost:8000/quizzes/complete/{attempt.id}/")
    print(f"🎯 Take More Quizzes: http://localhost:8000/quizzes/")
    
    return attempt

if __name__ == "__main__":
    demo_student_quiz()
