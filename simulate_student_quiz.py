#!/usr/bin/env python
import os
import django
from datetime import datetime

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'eco_learning_platform.settings')
django.setup()

from django.contrib.auth import get_user_model
from quizzes.models import Quiz, QuizAttempt, UserAnswer, Question, Answer
from django.utils import timezone

User = get_user_model()

def simulate_student_taking_quiz():
    """Simulate a student taking a quiz on the website"""
    
    print("🎓 STUDENT QUIZ SIMULATION")
    print("=" * 50)
    
    # Get the test student user
    try:
        student = User.objects.get(username='testuser')
        print(f"👤 Student: {student.username} (Level {student.level})")
        print(f"💰 Current Tokens: {student.total_eco_tokens}")
        print(f"⭐ Experience: {student.experience_points}")
    except User.DoesNotExist:
        print("❌ Test user not found. Please run setup_test_user.py first")
        return
    
    print("\n" + "=" * 50)
    print("📚 AVAILABLE QUIZZES")
    print("=" * 50)
    
    # Show available quizzes
    available_quizzes = Quiz.objects.filter(
        is_active=True,
        min_level_required__lte=student.level
    ).order_by('min_level_required')
    
    for i, quiz in enumerate(available_quizzes, 1):
        print(f"{i}. {quiz.title}")
        print(f"   📂 Category: {quiz.category.name}")
        print(f"   🎯 Difficulty: {quiz.get_difficulty_display()}")
        print(f"   💰 Rewards: {quiz.base_tokens_reward} + {quiz.perfect_score_bonus} bonus")
        print(f"   ⏱️  Time: {quiz.max_time_minutes} minutes")
        print()
    
    # Select the first available quiz (Sustainable Living Challenge)
    selected_quiz = available_quizzes.first()
    if not selected_quiz:
        print("❌ No quizzes available for this student level")
        return
    
    print("=" * 50)
    print(f"🎯 TAKING QUIZ: {selected_quiz.title}")
    print("=" * 50)
    
    # Create quiz attempt
    attempt = QuizAttempt.objects.create(
        user=student,
        quiz=selected_quiz,
        total_questions=selected_quiz.get_questions_count()
    )
    
    print(f"📝 Quiz attempt started at: {attempt.started_at}")
    print(f"❓ Total questions: {attempt.total_questions}")
    print()
    
    # Get quiz questions
    questions = list(selected_quiz.questions.all().order_by('order'))
    
    # Simulate answering questions (with realistic answers)
    correct_answers = 0
    
    # Predefined answers for the Sustainable Living quiz
    student_answers = [
        2,  # Question 1: Running the dishwasher (correct)
        1,  # Question 2: Eating less meat (correct) 
        2,  # Question 3: Bicycle (correct)
        2,  # Question 4: 75% less (correct)
        2,  # Question 5: Use reusable alternatives (correct)
        2   # Question 6: Heating/cooling system (correct)
    ]
    
    for i, question in enumerate(questions):
        print(f"Question {i+1}: {question.text}")
        
        # Get answer choices
        answers = list(question.answers.all().order_by('order'))
        for j, answer in enumerate(answers):
            marker = "✓" if j == student_answers[i] else " "
            print(f"  [{marker}] {j+1}. {answer.text}")
        
        # Select answer (using predefined answers)
        if i < len(student_answers):
            selected_answer_index = student_answers[i]
            selected_answer = answers[selected_answer_index]
        else:
            selected_answer = answers[0]  # Default to first answer
        
        # Create user answer
        is_correct = selected_answer.is_correct
        UserAnswer.objects.create(
            attempt=attempt,
            question=question,
            selected_answer=selected_answer,
            is_correct=is_correct
        )
        
        if is_correct:
            correct_answers += 1
            print(f"  ✅ Correct! {question.explanation}")
        else:
            print(f"  ❌ Incorrect. {question.explanation}")
        
        print()
    
    # Complete the quiz
    attempt.correct_answers = correct_answers
    attempt.calculate_score()
    attempt.is_completed = True
    attempt.completed_at = timezone.now()
    
    # Calculate time taken (simulate 8 minutes)
    time_taken_seconds = 8 * 60  # 8 minutes
    attempt.time_taken_seconds = time_taken_seconds
    
    # Calculate rewards
    base_tokens = selected_quiz.base_tokens_reward
    bonus_tokens = 0
    
    # Perfect score bonus
    if attempt.is_perfect_score():
        bonus_tokens += selected_quiz.perfect_score_bonus
    
    # Time bonus (if completed quickly)
    if selected_quiz.time_bonus_enabled and time_taken_seconds < (selected_quiz.max_time_minutes * 60 * 0.75):
        bonus_tokens += 5  # Quick completion bonus
    
    total_tokens = base_tokens + bonus_tokens
    attempt.tokens_earned = total_tokens
    attempt.experience_gained = total_tokens
    attempt.save()
    
    # Award tokens to student
    student.total_eco_tokens += total_tokens
    student.experience_points += total_tokens
    
    # Check for level up
    old_level = student.level
    if student.experience_points >= student.level * 100:  # Simple level calculation
        student.level += 1
    
    student.save()
    
    print("=" * 50)
    print("🎉 QUIZ COMPLETED!")
    print("=" * 50)
    print(f"📊 Score: {attempt.score:.1f}%")
    print(f"✅ Correct Answers: {correct_answers}/{attempt.total_questions}")
    print(f"⏱️  Time Taken: {time_taken_seconds // 60} minutes {time_taken_seconds % 60} seconds")
    print(f"💰 Tokens Earned: {total_tokens}")
    print(f"   - Base reward: {base_tokens}")
    print(f"   - Bonus: {bonus_tokens}")
    print(f"⭐ Experience Gained: {attempt.experience_gained}")
    
    if student.level > old_level:
        print(f"🎊 LEVEL UP! New level: {student.level}")
    
    print(f"\n👤 Updated Student Stats:")
    print(f"   💰 Total Tokens: {student.total_eco_tokens}")
    print(f"   ⭐ Experience: {student.experience_points}")
    print(f"   🏆 Level: {student.level}")
    
    print(f"\n🌐 View results on website: http://localhost:8000/quizzes/complete/{attempt.id}/")
    
    return attempt

if __name__ == "__main__":
    simulate_student_taking_quiz()
