#!/usr/bin/env python
import os
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'eco_learning_platform.settings')
django.setup()

from quizzes.models import QuizCategory, Quiz, Question, Answer
from django.contrib.auth import get_user_model

User = get_user_model()

print("🔧 COMPREHENSIVE QUIZ SETUP")
print("=" * 60)

# Clear existing data
print("🗑️ Clearing existing quiz data...")
Answer.objects.all().delete()
Question.objects.all().delete()
Quiz.objects.all().delete()
QuizCategory.objects.all().delete()

# Create categories
print("📂 Creating quiz categories...")
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

biodiversity_cat = QuizCategory.objects.create(
    name="Biodiversity & Conservation",
    description="Protecting wildlife and natural ecosystems",
    icon="🦋",
    color="#6f42c1",
    is_active=True
)

print(f"✅ Created {QuizCategory.objects.count()} categories")

# Create Climate Change Quiz
print("📝 Creating Climate Change quiz...")
climate_quiz = Quiz.objects.create(
    title="Climate Change Fundamentals",
    description="Test your knowledge about the basics of climate change, its causes, and effects on our planet.",
    category=climate_cat,
    difficulty="beginner",
    base_tokens_reward=25,
    perfect_score_bonus=15,
    time_bonus_enabled=True,
    max_time_minutes=12,
    min_level_required=1,
    is_active=True,
    is_featured=True,
    randomize_questions=True,
    show_correct_answers=True,
)

# Climate Quiz Questions
q1 = Question.objects.create(
    quiz=climate_quiz,
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

q2 = Question.objects.create(
    quiz=climate_quiz,
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

q3 = Question.objects.create(
    quiz=climate_quiz,
    question_type="true_false",
    text="Global temperatures have risen by approximately 1.1°C since pre-industrial times.",
    explanation="True. Global average temperatures have increased by about 1.1°C since the late 1800s.",
    points=1,
    order=3
)

Answer.objects.create(question=q3, text="True", is_correct=True, order=1)
Answer.objects.create(question=q3, text="False", is_correct=False, order=2)

q4 = Question.objects.create(
    quiz=climate_quiz,
    question_type="multiple_choice",
    text="What percentage of climate scientists agree that human activities are the primary cause of recent climate change?",
    explanation="Over 97% of actively publishing climate scientists agree that human activities are the primary cause of recent climate change.",
    points=1,
    order=4
)

Answer.objects.create(question=q4, text="About 50%", is_correct=False, order=1)
Answer.objects.create(question=q4, text="About 75%", is_correct=False, order=2)
Answer.objects.create(question=q4, text="Over 97%", is_correct=True, order=3)
Answer.objects.create(question=q4, text="100%", is_correct=False, order=4)

# Create Energy Quiz
print("⚡ Creating Renewable Energy quiz...")
energy_quiz = Quiz.objects.create(
    title="Sustainable Living Challenge",
    description="Learn about solar power, wind energy, and other renewable technologies that power our future.",
    category=energy_cat,
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

eq1 = Question.objects.create(
    quiz=energy_quiz,
    question_type="multiple_choice",
    text="What does 'PV' stand for in solar energy?",
    explanation="PV stands for Photovoltaic, which refers to the technology that converts sunlight directly into electricity.",
    points=1,
    order=1
)

Answer.objects.create(question=eq1, text="Power Voltage", is_correct=False, order=1)
Answer.objects.create(question=eq1, text="Photovoltaic", is_correct=True, order=2)
Answer.objects.create(question=eq1, text="Positive Voltage", is_correct=False, order=3)
Answer.objects.create(question=eq1, text="Panel Voltage", is_correct=False, order=4)

eq2 = Question.objects.create(
    quiz=energy_quiz,
    question_type="multiple_choice",
    text="Which renewable energy source is most widely used globally?",
    explanation="Hydroelectric power is the most widely used renewable energy source globally, providing about 16% of world electricity.",
    points=1,
    order=2
)

Answer.objects.create(question=eq2, text="Solar", is_correct=False, order=1)
Answer.objects.create(question=eq2, text="Wind", is_correct=False, order=2)
Answer.objects.create(question=eq2, text="Hydroelectric", is_correct=True, order=3)
Answer.objects.create(question=eq2, text="Geothermal", is_correct=False, order=4)

eq3 = Question.objects.create(
    quiz=energy_quiz,
    question_type="true_false",
    text="Wind turbines can generate electricity even in light winds.",
    explanation="True. Modern wind turbines can start generating electricity at wind speeds as low as 3-4 mph (5-6 km/h).",
    points=1,
    order=3
)

Answer.objects.create(question=eq3, text="True", is_correct=True, order=1)
Answer.objects.create(question=eq3, text="False", is_correct=False, order=2)

# Create Waste Management Quiz
print("♻️ Creating Waste Management quiz...")
waste_quiz = Quiz.objects.create(
    title="Waste Reduction & Recycling",
    description="Master the art of reducing waste, recycling effectively, and living sustainably.",
    category=waste_cat,
    difficulty="intermediate",
    base_tokens_reward=30,
    perfect_score_bonus=20,
    time_bonus_enabled=True,
    max_time_minutes=15,
    min_level_required=2,
    is_active=True,
    is_featured=False,
    randomize_questions=True,
    show_correct_answers=True,
)

wq1 = Question.objects.create(
    quiz=waste_quiz,
    question_type="multiple_choice",
    text="What does the '3 Rs' of waste management stand for?",
    explanation="The 3 Rs stand for Reduce, Reuse, and Recycle - the hierarchy of waste management practices.",
    points=1,
    order=1
)

Answer.objects.create(question=wq1, text="Reduce, Reuse, Recycle", is_correct=True, order=1)
Answer.objects.create(question=wq1, text="Remove, Replace, Restore", is_correct=False, order=2)
Answer.objects.create(question=wq1, text="Refuse, Reduce, Recycle", is_correct=False, order=3)
Answer.objects.create(question=wq1, text="Repair, Reuse, Recycle", is_correct=False, order=4)

# Create Biodiversity Quiz
print("🦋 Creating Biodiversity quiz...")
bio_quiz = Quiz.objects.create(
    title="Protecting Our Planet's Wildlife",
    description="Explore the importance of biodiversity and learn how to protect endangered species.",
    category=biodiversity_cat,
    difficulty="advanced",
    base_tokens_reward=40,
    perfect_score_bonus=25,
    time_bonus_enabled=True,
    max_time_minutes=20,
    min_level_required=3,
    is_active=True,
    is_featured=False,
    randomize_questions=True,
    show_correct_answers=True,
)

bq1 = Question.objects.create(
    quiz=bio_quiz,
    question_type="multiple_choice",
    text="What percentage of known species are currently threatened with extinction?",
    explanation="According to the IUCN Red List, approximately 25% of known species are currently threatened with extinction.",
    points=1,
    order=1
)

Answer.objects.create(question=bq1, text="10%", is_correct=False, order=1)
Answer.objects.create(question=bq1, text="25%", is_correct=True, order=2)
Answer.objects.create(question=bq1, text="50%", is_correct=False, order=3)
Answer.objects.create(question=bq1, text="75%", is_correct=False, order=4)

print("\n🎯 FINAL DATABASE STATUS:")
print("=" * 60)
print(f"📂 Categories: {QuizCategory.objects.count()}")
print(f"📝 Quizzes: {Quiz.objects.count()}")
print(f"❓ Questions: {Question.objects.count()}")
print(f"💬 Answers: {Answer.objects.count()}")
print()

for cat in QuizCategory.objects.all():
    print(f"   {cat.icon} {cat.name}: {cat.quizzes.count()} quiz(es)")
    for quiz in cat.quizzes.all():
        featured = "⭐ " if quiz.is_featured else "   "
        print(f"     {featured}{quiz.title} ({quiz.get_questions_count()} questions)")

print("\n✨ QUIZ SETUP COMPLETE!")
print("🌐 Start your Django server with: python manage.py runserver")
print("🎯 Visit: http://localhost:8000/quizzes/")
print("📚 Quizzes should now be visible on your website!")
