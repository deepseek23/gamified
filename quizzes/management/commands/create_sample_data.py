from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from quizzes.models import QuizCategory, Quiz, Question, Answer
from eco_tasks.models import TaskCategory, EcoTask
from rewards.models import RewardItem, TokenEarningRule

User = get_user_model()

class Command(BaseCommand):
    help = 'Create sample data for the eco-learning platform'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing data before creating new data',
        )

    def handle(self, *args, **options):
        if options['clear']:
            self.stdout.write('Clearing existing data...')
            QuizCategory.objects.all().delete()
            TaskCategory.objects.all().delete()
            RewardItem.objects.all().delete()
            TokenEarningRule.objects.all().delete()

        self.create_quiz_categories()
        self.create_quizzes()
        self.create_task_categories()
        self.create_eco_tasks()
        self.create_rewards()
        self.create_token_rules()
        
        self.stdout.write(
            self.style.SUCCESS('Successfully created sample data!')
        )

    def create_quiz_categories(self):
        categories = [
            {
                'name': 'Climate Change Basics',
                'description': 'Learn the fundamentals of climate change and global warming',
                'icon': '🌡️',
                'color': '#dc3545'
            },
            {
                'name': 'Renewable Energy',
                'description': 'Explore sustainable energy sources and technologies',
                'icon': '⚡',
                'color': '#ffc107'
            },
            {
                'name': 'Waste Management',
                'description': 'Understanding recycling, composting, and waste reduction',
                'icon': '♻️',
                'color': '#28a745'
            },
            {
                'name': 'Biodiversity',
                'description': 'Learn about ecosystems, wildlife conservation, and species protection',
                'icon': '🦋',
                'color': '#17a2b8'
            }
        ]
        
        for cat_data in categories:
            category, created = QuizCategory.objects.get_or_create(
                name=cat_data['name'],
                defaults=cat_data
            )
            if created:
                self.stdout.write(f'Created quiz category: {category.name}')

    def create_quizzes(self):
        climate_category = QuizCategory.objects.get(name='Climate Change Basics')
        
        quiz, created = Quiz.objects.get_or_create(
            title='Climate Change Fundamentals',
            defaults={
                'description': 'Test your knowledge about the basics of climate change, its causes, and effects on our planet.',
                'category': climate_category,
                'difficulty': 'beginner',
                'base_tokens_reward': 20,
                'perfect_score_bonus': 10,
                'time_bonus_enabled': True,
                'max_time_minutes': 10,
                'min_level_required': 1,
                'is_active': True,
                'is_featured': True,
                'randomize_questions': True,
                'show_correct_answers': True,
            }
        )
        
        if created:
            self.stdout.write(f'Created quiz: {quiz.title}')
            self.create_climate_questions(quiz)

    def create_climate_questions(self, quiz):
        questions_data = [
            {
                'text': 'What is the primary cause of climate change?',
                'explanation': 'Human activities, particularly burning fossil fuels, release greenhouse gases that trap heat in the atmosphere.',
                'answers': [
                    ('Natural climate variations', False),
                    ('Human activities releasing greenhouse gases', True),
                    ('Solar radiation changes', False),
                    ('Ocean currents', False)
                ]
            },
            {
                'text': 'Which greenhouse gas is most abundant in the atmosphere?',
                'explanation': 'Carbon dioxide (CO2) is the most abundant greenhouse gas, primarily from burning fossil fuels.',
                'answers': [
                    ('Methane (CH4)', False),
                    ('Carbon dioxide (CO2)', True),
                    ('Nitrous oxide (N2O)', False),
                    ('Fluorinated gases', False)
                ]
            },
            {
                'text': 'Global temperatures have risen by approximately 1.1°C since pre-industrial times.',
                'explanation': 'True. Global average temperatures have increased by about 1.1°C since the late 1800s.',
                'question_type': 'true_false',
                'answers': [
                    ('True', True),
                    ('False', False)
                ]
            }
        ]
        
        for i, q_data in enumerate(questions_data, 1):
            question = Question.objects.create(
                quiz=quiz,
                question_type=q_data.get('question_type', 'multiple_choice'),
                text=q_data['text'],
                explanation=q_data['explanation'],
                points=1,
                order=i
            )
            
            for j, (answer_text, is_correct) in enumerate(q_data['answers'], 1):
                Answer.objects.create(
                    question=question,
                    text=answer_text,
                    is_correct=is_correct,
                    order=j
                )

    def create_task_categories(self):
        categories = [
            {
                'name': 'Energy Conservation',
                'description': 'Tasks focused on reducing energy consumption at home and school',
                'icon': '💡',
                'color': '#ffc107'
            },
            {
                'name': 'Waste Reduction',
                'description': 'Activities to minimize waste and promote recycling',
                'icon': '🗂️',
                'color': '#28a745'
            },
            {
                'name': 'Water Conservation',
                'description': 'Tasks to conserve and protect water resources',
                'icon': '💧',
                'color': '#17a2b8'
            },
            {
                'name': 'Green Transportation',
                'description': 'Eco-friendly transportation and mobility tasks',
                'icon': '🚲',
                'color': '#20c997'
            }
        ]
        
        for cat_data in categories:
            category, created = TaskCategory.objects.get_or_create(
                name=cat_data['name'],
                defaults=cat_data
            )
            if created:
                self.stdout.write(f'Created task category: {category.name}')

    def create_eco_tasks(self):
        energy_category = TaskCategory.objects.get(name='Energy Conservation')
        
        task, created = EcoTask.objects.get_or_create(
            title='LED Light Audit',
            defaults={
                'description': 'Conduct an audit of your home lighting and identify opportunities to switch to LED bulbs.',
                'category': energy_category,
                'difficulty': 'easy',
                'task_type': 'individual',
                'instructions': '''1. Walk through your home and count all light bulbs
2. Identify which ones are not LED bulbs
3. Calculate potential energy savings
4. Take photos of different bulb types
5. Create a plan for LED replacement''',
                'materials_needed': 'Notebook, pen, camera/phone, measuring tape (optional)',
                'estimated_time_minutes': 30,
                'verification_method': 'photo',
                'verification_instructions': 'Take photos showing different types of bulbs in your home and submit a brief report of your findings.',
                'requires_approval': True,
                'base_tokens_reward': 25,
                'experience_points': 15,
                'min_level_required': 1,
                'is_active': True,
                'is_featured': True
            }
        )
        
        if created:
            self.stdout.write(f'Created eco-task: {task.title}')

    def create_rewards(self):
        rewards_data = [
            {
                'name': 'Eco Warrior Badge',
                'description': 'A digital badge recognizing your commitment to environmental action',
                'item_type': 'badge',
                'cost_tokens': 50,
                'min_level_required': 2
            },
            {
                'name': 'Plant a Tree Donation',
                'description': 'We will plant a tree in your name through our partner organizations',
                'item_type': 'tree_planting',
                'cost_tokens': 100,
                'min_level_required': 3
            },
            {
                'name': 'Environmental Achievement Certificate',
                'description': 'A personalized certificate recognizing your environmental learning achievements',
                'item_type': 'certificate',
                'cost_tokens': 75,
                'min_level_required': 2
            }
        ]
        
        for reward_data in rewards_data:
            reward, created = RewardItem.objects.get_or_create(
                name=reward_data['name'],
                defaults=reward_data
            )
            if created:
                self.stdout.write(f'Created reward: {reward.name}')

    def create_token_rules(self):
        rules_data = [
            {
                'activity': 'quiz_completion',
                'base_tokens': 10,
                'bonus_multiplier': 1.5,
                'level_multiplier': True
            },
            {
                'activity': 'quiz_perfect',
                'base_tokens': 20,
                'bonus_multiplier': 2.0,
                'level_multiplier': True
            },
            {
                'activity': 'task_completion',
                'base_tokens': 15,
                'bonus_multiplier': 1.2,
                'level_multiplier': True
            },
            {
                'activity': 'daily_login',
                'base_tokens': 5,
                'bonus_multiplier': 1.0,
                'streak_required': 7
            }
        ]
        
        for rule_data in rules_data:
            rule, created = TokenEarningRule.objects.get_or_create(
                activity=rule_data['activity'],
                defaults=rule_data
            )
            if created:
                self.stdout.write(f'Created token rule: {rule.get_activity_display()}')
