#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'eco_learning_platform.settings')
django.setup()

from quizzes.models import QuizCategory, Quiz, Question, Answer

print("🔍 CHECKING DATABASE STATUS")
print("=" * 50)

# Check current data
categories = QuizCategory.objects.all()
quizzes = Quiz.objects.all()

print(f"📂 Categories in database: {categories.count()}")
print(f"📝 Quizzes in database: {quizzes.count()}")

if categories.exists():
    for cat in categories:
        print(f"   - {cat.name}: {cat.quizzes.count()} quizzes")
else:
    print("❌ No categories found - creating sample data...")
    
    # Create categories
    climate_cat = QuizCategory.objects.create(
        name="Climate Change Basics",
        description="Learn the fundamentals of climate change and global warming",
        icon="🌡️",
        color="#dc3545",
        is_active=True
    )
    
    energy_cat = QuizCategory.objects.create(
        name="Renewable Energy",
        description="Explore sustainable energy sources and technologies",
        icon="⚡",
        color="#ffc107",
        is_active=True
    )
    
    waste_cat = QuizCategory.objects.create(
        name="Waste Management",
        description="Understanding recycling, composting, and waste reduction",
        icon="♻️",
        color="#28a745",
        is_active=True
    )
    
    print("✅ Created 3 categories")
    
    # Create a simple quiz
    quiz = Quiz.objects.create(
        title="Climate Change Fundamentals",
        description="Test your knowledge about the basics of climate change, its causes, and effects on our planet.",
        category=climate_cat,
        difficulty="beginner",
        base_tokens_reward=20,
        perfect_score_bonus=10,
        time_bonus_enabled=True,
        max_time_minutes=10,
        min_level_required=1,
        is_active=True,
        is_featured=True,
        randomize_questions=True,
        show_correct_answers=True,
    )
    
    # Create questions
    q1 = Question.objects.create(
        quiz=quiz,
        question_type="multiple_choice",
        text="What is the primary cause of climate change?",
        explanation="Human activities, particularly burning fossil fuels, release greenhouse gases that trap heat in the atmosphere.",
        points=1,
        order=1
    )
    
    # Create answers
    Answer.objects.create(question=q1, text="Natural climate variations", is_correct=False, order=1)
    Answer.objects.create(question=q1, text="Human activities releasing greenhouse gases", is_correct=True, order=2)
    Answer.objects.create(question=q1, text="Solar radiation changes", is_correct=False, order=3)
    Answer.objects.create(question=q1, text="Ocean currents", is_correct=False, order=4)
    
    q2 = Question.objects.create(
        quiz=quiz,
        question_type="true_false",
        text="Global temperatures have risen by approximately 1.1°C since pre-industrial times.",
        explanation="True. Global average temperatures have increased by about 1.1°C since the late 1800s.",
        points=1,
        order=2
    )
    
    Answer.objects.create(question=q2, text="True", is_correct=True, order=1)
    Answer.objects.create(question=q2, text="False", is_correct=False, order=2)
    
    print("✅ Created sample quiz with 2 questions")

print("\n🔄 FINAL STATUS:")
print(f"📂 Total Categories: {QuizCategory.objects.count()}")
print(f"📝 Total Quizzes: {Quiz.objects.count()}")
print(f"❓ Total Questions: {Question.objects.count()}")
print(f"💬 Total Answers: {Answer.objects.count()}")

print("\n🌐 Refresh your browser at: http://localhost:8000/quizzes/")
