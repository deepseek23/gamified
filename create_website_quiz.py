#!/usr/bin/env python
import os
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'eco_learning_platform.settings')
django.setup()

from quizzes.models import QuizCategory, Quiz, Question, Answer

def create_sustainable_living_quiz():
    """Create a new Sustainable Living quiz for the website"""
    
    # Get or create category
    category, created = QuizCategory.objects.get_or_create(
        name="Sustainable Living",
        defaults={
            'description': 'Learn about sustainable practices for daily life and eco-friendly choices',
            'icon': '🌱',
            'color': '#20c997',
            'is_active': True
        }
    )
    
    if created:
        print(f"✅ Created new category: {category.name}")
    else:
        print(f"📂 Using existing category: {category.name}")
    
    # Create the quiz
    quiz, created = Quiz.objects.get_or_create(
        title="Sustainable Living Challenge",
        defaults={
            'description': 'Test your knowledge about sustainable living practices, eco-friendly choices, and green lifestyle tips that can make a real difference for our planet.',
            'category': category,
            'difficulty': 'beginner',
            'base_tokens_reward': 30,
            'perfect_score_bonus': 15,
            'time_bonus_enabled': True,
            'max_time_minutes': 12,
            'min_level_required': 1,
            'is_active': True,
            'is_featured': True,
            'randomize_questions': True,
            'show_correct_answers': True,
        }
    )
    
    if created:
        print(f"🎯 Created new quiz: {quiz.title}")
    else:
        print(f"📝 Quiz already exists: {quiz.title}")
        return quiz
    
    # Quiz questions and answers
    questions_data = [
        {
            'text': 'Which of the following uses the least water?',
            'explanation': 'Taking a 5-minute shower uses about 25 gallons of water, while a bath uses 70 gallons, dishwasher uses 6 gallons, and washing machine uses 40 gallons.',
            'answers': [
                ('Taking a 5-minute shower', False),
                ('Taking a bath', False),
                ('Running the dishwasher', True),
                ('Using the washing machine', False)
            ]
        },
        {
            'text': 'What is the most effective way to reduce your carbon footprint from food?',
            'explanation': 'Eating less meat, especially beef, has the biggest impact on reducing food-related carbon emissions. Livestock farming produces significant greenhouse gases.',
            'answers': [
                ('Buying organic food only', False),
                ('Eating less meat', True),
                ('Avoiding all processed foods', False),
                ('Growing your own vegetables', False)
            ]
        },
        {
            'text': 'Which transportation method produces the lowest CO2 emissions per mile?',
            'explanation': 'Bicycles produce zero direct emissions and are the most environmentally friendly transportation option for short to medium distances.',
            'answers': [
                ('Electric car', False),
                ('Public bus', False),
                ('Bicycle', True),
                ('Hybrid car', False)
            ]
        },
        {
            'text': 'LED light bulbs use approximately how much less energy than incandescent bulbs?',
            'explanation': 'LED bulbs use about 75% less energy than traditional incandescent bulbs and last 25 times longer, making them highly efficient.',
            'answers': [
                ('25% less', False),
                ('50% less', False),
                ('75% less', True),
                ('90% less', False)
            ]
        },
        {
            'text': 'What is the best way to reduce plastic waste at home?',
            'explanation': 'Using reusable bags, bottles, and containers prevents single-use plastics from entering the waste stream and reduces overall plastic consumption.',
            'answers': [
                ('Recycle all plastic items', False),
                ('Buy biodegradable plastics', False),
                ('Use reusable alternatives', True),
                ('Burn plastic waste safely', False)
            ]
        },
        {
            'text': 'Which household appliance typically uses the most electricity?',
            'explanation': 'Heating and cooling systems (HVAC) typically account for about 50% of home energy use, making them the largest electricity consumers.',
            'answers': [
                ('Refrigerator', False),
                ('Water heater', False),
                ('Heating/cooling system', True),
                ('Television', False)
            ]
        }
    ]
    
    # Create questions and answers
    for i, q_data in enumerate(questions_data, 1):
        question = Question.objects.create(
            quiz=quiz,
            question_type='multiple_choice',
            text=q_data['text'],
            explanation=q_data['explanation'],
            points=1,
            order=i
        )
        
        # Create answers
        for j, (answer_text, is_correct) in enumerate(q_data['answers'], 1):
            Answer.objects.create(
                question=question,
                text=answer_text,
                is_correct=is_correct,
                order=j
            )
        
        print(f"  ➕ Added question {i}: {q_data['text'][:50]}...")
    
    print(f"\n🎉 Successfully created quiz '{quiz.title}' with {len(questions_data)} questions!")
    print(f"💰 Rewards: {quiz.base_tokens_reward} base tokens + {quiz.perfect_score_bonus} perfect bonus")
    print(f"⏱️  Time limit: {quiz.max_time_minutes} minutes")
    print(f"🎯 Difficulty: {quiz.get_difficulty_display()}")
    print(f"\n🌐 Quiz is now live on your website at: http://localhost:8000/quizzes/")
    
    return quiz

if __name__ == "__main__":
    print("🚀 Creating new quiz for your website...\n")
    quiz = create_sustainable_living_quiz()
    print("\n✨ Quiz creation complete! Check your website to see the new quiz.")
