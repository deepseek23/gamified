#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'eco_learning_platform.settings')
django.setup()

from quizzes.models import QuizCategory, Quiz, Question, Answer

print("🔧 FIXING QUIZ DISPLAY ISSUE")
print("=" * 50)

# Clear existing data first
QuizCategory.objects.all().delete()
Quiz.objects.all().delete()
Question.objects.all().delete()
Answer.objects.all().delete()

print("🗑️ Cleared existing data")

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

# Create Climate Change quiz
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

print("✅ Created featured quiz")

# Question 1
q1 = Question.objects.create(
    quiz=quiz,
    question_type="multiple_choice",
    text="What is the primary cause of climate change?",
    explanation="Human activities, particularly burning fossil fuels, release greenhouse gases that trap heat in the atmosphere.",
    points=1,
    order=1
)

Answer.objects.create(question=q1, text="Natural climate variations", is_correct=False, order=1)
Answer.objects.create(question=q1, text="Human activities releasing greenhouse gases", is_correct=True, order=2)
Answer.objects.create(question=q1, text="Solar radiation changes", is_correct=False, order=3)
Answer.objects.create(question=q1, text="Ocean currents", is_correct=False, order=4)

# Question 2
q2 = Question.objects.create(
    quiz=quiz,
    question_type="multiple_choice",
    text="Which greenhouse gas is most abundant in the atmosphere?",
    explanation="Carbon dioxide (CO2) is the most abundant greenhouse gas, primarily from burning fossil fuels.",
    points=1,
    order=2
)

Answer.objects.create(question=q2, text="Methane (CH4)", is_correct=False, order=1)
Answer.objects.create(question=q2, text="Carbon dioxide (CO2)", is_correct=True, order=2)
Answer.objects.create(question=q2, text="Nitrous oxide (N2O)", is_correct=False, order=3)
Answer.objects.create(question=q2, text="Fluorinated gases", is_correct=False, order=4)

# Question 3
q3 = Question.objects.create(
    quiz=quiz,
    question_type="true_false",
    text="Global temperatures have risen by approximately 1.1°C since pre-industrial times.",
    explanation="True. Global average temperatures have increased by about 1.1°C since the late 1800s.",
    points=1,
    order=3
)

Answer.objects.create(question=q3, text="True", is_correct=True, order=1)
Answer.objects.create(question=q3, text="False", is_correct=False, order=2)

print("✅ Created 3 questions with answers")

# Create second quiz for Energy category
energy_quiz = Quiz.objects.create(
    title="Solar Energy Basics",
    description="Learn about solar power and renewable energy technologies.",
    category=energy_cat,
    difficulty="beginner",
    base_tokens_reward=15,
    perfect_score_bonus=8,
    time_bonus_enabled=True,
    max_time_minutes=8,
    min_level_required=1,
    is_active=True,
    is_featured=False,
    randomize_questions=True,
    show_correct_answers=True,
)

# Solar question
solar_q = Question.objects.create(
    quiz=energy_quiz,
    question_type="multiple_choice",
    text="What does 'PV' stand for in solar energy?",
    explanation="PV stands for Photovoltaic, which refers to the technology that converts sunlight directly into electricity.",
    points=1,
    order=1
)

Answer.objects.create(question=solar_q, text="Power Voltage", is_correct=False, order=1)
Answer.objects.create(question=solar_q, text="Photovoltaic", is_correct=True, order=2)
Answer.objects.create(question=solar_q, text="Positive Voltage", is_correct=False, order=3)
Answer.objects.create(question=solar_q, text="Panel Voltage", is_correct=False, order=4)

print("✅ Created second quiz")

print("\n🎯 FINAL STATUS:")
print(f"📂 Categories: {QuizCategory.objects.count()}")
print(f"📝 Quizzes: {Quiz.objects.count()}")
print(f"❓ Questions: {Question.objects.count()}")
print(f"💬 Answers: {Answer.objects.count()}")

for cat in QuizCategory.objects.all():
    print(f"   - {cat.name}: {cat.quizzes.count()} quiz(es)")

print("\n🌐 Now refresh: http://localhost:8000/quizzes/")
print("✨ Quizzes should now appear on the website!")
