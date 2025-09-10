from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
import json
import uuid
import re
from .models import (
    ChatSession, ChatMessage, BotKnowledgeBase, 
    ChatbotIntent, UserFeedback
)

@login_required
def chat_interface(request):
    """Main chat interface"""
    # Get or create active session
    active_session = ChatSession.objects.filter(
        user=request.user, 
        is_active=True
    ).first()
    
    if not active_session:
        active_session = ChatSession.objects.create(
            user=request.user,
            session_id=str(uuid.uuid4())
        )
    
    # Get recent messages
    recent_messages = ChatMessage.objects.filter(
        session=active_session
    ).order_by('timestamp')[:50]
    
    context = {
        'session': active_session,
        'messages': recent_messages,
    }
    return render(request, 'chatbot/chat.html', context)

@login_required
@require_POST
def send_message(request):
    """Handle user messages and generate bot responses"""
    data = json.loads(request.body)
    user_message = data.get('message', '').strip()
    
    if not user_message:
        return JsonResponse({'error': 'Empty message'}, status=400)
    
    # Get or create session
    session = ChatSession.objects.filter(
        user=request.user, 
        is_active=True
    ).first()
    
    if not session:
        session = ChatSession.objects.create(
            user=request.user,
            session_id=str(uuid.uuid4())
        )
    
    # Save user message
    user_msg = ChatMessage.objects.create(
        session=session,
        message_type='user',
        content=user_message
    )
    
    # Generate bot response
    bot_response = generate_bot_response(user_message, session)
    
    # Save bot message
    bot_msg = ChatMessage.objects.create(
        session=session,
        message_type='bot',
        content=bot_response['content'],
        confidence_score=bot_response.get('confidence', 0.8),
        intent_detected=bot_response.get('intent', ''),
        entities_extracted=bot_response.get('entities', {})
    )
    
    # Update session
    session.last_activity = timezone.now()
    session.current_topic = bot_response.get('topic', session.current_topic)
    session.save()
    
    return JsonResponse({
        'bot_response': bot_response['content'],
        'message_id': bot_msg.id,
        'intent': bot_response.get('intent', ''),
        'suggestions': bot_response.get('suggestions', [])
    })

def generate_bot_response(user_message, session):
    """Generate appropriate bot response based on user message"""
    user_message_lower = user_message.lower()
    
    # Check for specific intents
    intent = detect_intent(user_message_lower)
    
    # Generate response based on intent
    if intent == 'greeting':
        return {
            'content': f"Hello {session.user.first_name or session.user.username}! 🌱 I'm EcoBot, your environmental learning assistant. How can I help you today?",
            'intent': intent,
            'suggestions': ['Show my progress', 'Find quizzes', 'Suggest eco-tasks', 'Explain rewards']
        }
    
    elif intent == 'progress_inquiry':
        return generate_progress_response(session.user)
    
    elif intent == 'quiz_help':
        return generate_quiz_help_response(user_message_lower)
    
    elif intent == 'task_help':
        return generate_task_help_response(user_message_lower)
    
    elif intent == 'rewards_inquiry':
        return generate_rewards_response(session.user)
    
    elif intent == 'eco_facts':
        return generate_eco_fact_response()
    
    else:
        # Search knowledge base
        kb_response = search_knowledge_base(user_message_lower)
        if kb_response:
            return kb_response
        
        # Default response
        return {
            'content': "I'm not sure I understand that question. Could you try rephrasing it? I can help you with quizzes, eco-tasks, your progress, rewards, or environmental facts! 🤔",
            'intent': 'unknown',
            'suggestions': ['Show my stats', 'Available quizzes', 'My tasks', 'Eco tips']
        }

def detect_intent(message):
    """Simple intent detection based on keywords"""
    greetings = ['hello', 'hi', 'hey', 'good morning', 'good afternoon']
    progress_words = ['progress', 'stats', 'level', 'tokens', 'score', 'achievements']
    quiz_words = ['quiz', 'question', 'test', 'exam']
    task_words = ['task', 'activity', 'challenge', 'mission']
    reward_words = ['reward', 'token', 'point', 'prize', 'redeem']
    fact_words = ['fact', 'learn', 'environment', 'climate', 'nature', 'eco']
    
    if any(word in message for word in greetings):
        return 'greeting'
    elif any(word in message for word in progress_words):
        return 'progress_inquiry'
    elif any(word in message for word in quiz_words):
        return 'quiz_help'
    elif any(word in message for word in task_words):
        return 'task_help'
    elif any(word in message for word in reward_words):
        return 'rewards_inquiry'
    elif any(word in message for word in fact_words):
        return 'eco_facts'
    
    return 'unknown'

def generate_progress_response(user):
    """Generate response about user's progress"""
    from accounts.models import UserProfile
    
    profile, _ = UserProfile.objects.get_or_create(user=user)
    
    response = f"Here's your eco-learning progress! 📊\n\n"
    response += f"🏆 Level: {user.level}\n"
    response += f"🪙 Eco-tokens: {user.total_eco_tokens}\n"
    response += f"📚 Quizzes completed: {profile.quizzes_completed}\n"
    response += f"✅ Tasks completed: {profile.tasks_completed}\n"
    response += f"🔥 Current streak: {profile.streak_days} days\n"
    
    if profile.average_quiz_score > 0:
        response += f"📈 Average quiz score: {profile.average_quiz_score:.1f}%\n"
    
    response += f"\nKeep up the great work! 🌟"
    
    return {
        'content': response,
        'intent': 'progress_inquiry',
        'suggestions': ['Take a quiz', 'Find new tasks', 'View leaderboards']
    }

def generate_quiz_help_response(message):
    """Generate response about quizzes"""
    from quizzes.models import Quiz, QuizCategory
    
    if 'available' in message or 'find' in message:
        quiz_count = Quiz.objects.filter(is_active=True).count()
        categories = QuizCategory.objects.filter(is_active=True)[:3]
        
        response = f"There are {quiz_count} quizzes available! 📚\n\n"
        response += "Popular categories:\n"
        for cat in categories:
            response += f"• {cat.name} {cat.icon}\n"
        
        response += "\nQuizzes help you earn eco-tokens and level up! 🚀"
    else:
        response = "Quizzes are a fun way to learn about the environment! 🧠\n\n"
        response += "• Complete quizzes to earn eco-tokens\n"
        response += "• Perfect scores give bonus rewards\n"
        response += "• Compete on leaderboards\n"
        response += "• Learn fascinating eco-facts!"
    
    return {
        'content': response,
        'intent': 'quiz_help',
        'suggestions': ['Browse quizzes', 'My quiz history', 'Quiz leaderboards']
    }

def generate_task_help_response(message):
    """Generate response about eco-tasks"""
    from eco_tasks.models import EcoTask, TaskCategory
    
    if 'available' in message or 'find' in message:
        task_count = EcoTask.objects.filter(is_active=True).count()
        categories = TaskCategory.objects.filter(is_active=True)[:3]
        
        response = f"There are {task_count} eco-tasks waiting for you! 🌍\n\n"
        response += "Categories include:\n"
        for cat in categories:
            response += f"• {cat.name} {cat.icon}\n"
        
        response += "\nReal-world actions that make a difference! 💪"
    else:
        response = "Eco-tasks are real-world environmental actions! 🌱\n\n"
        response += "• Complete tasks to earn tokens\n"
        response += "• Make a real environmental impact\n"
        response += "• Share your progress with photos\n"
        response += "• Join challenges with friends!"
    
    return {
        'content': response,
        'intent': 'task_help',
        'suggestions': ['Browse tasks', 'My active tasks', 'Join challenges']
    }

def generate_rewards_response(user):
    """Generate response about rewards"""
    from rewards.models import RewardItem
    
    available_rewards = RewardItem.objects.filter(is_active=True).count()
    
    response = f"You have {user.total_eco_tokens} eco-tokens! 🪙\n\n"
    response += f"There are {available_rewards} rewards available in the store:\n"
    response += "• Event discounts 🎫\n"
    response += "• Special badges 🏅\n"
    response += "• Environmental donations 🌳\n"
    response += "• Eco merchandise 👕\n\n"
    response += "Earn more tokens by completing quizzes and tasks!"
    
    return {
        'content': response,
        'intent': 'rewards_inquiry',
        'suggestions': ['Visit reward store', 'My rewards', 'Earn more tokens']
    }

def generate_eco_fact_response():
    """Generate an environmental fact"""
    facts = [
        "🌍 Did you know? A single tree can absorb 48 pounds of CO2 per year!",
        "♻️ Recycling one aluminum can saves enough energy to power a TV for 3 hours!",
        "🌊 The ocean produces over 50% of the world's oxygen!",
        "🐝 Bees pollinate about 1/3 of everything we eat!",
        "🌱 Bamboo is the fastest-growing plant on Earth - it can grow 3 feet in 24 hours!",
        "💡 LED bulbs use 75% less energy than traditional incandescent bulbs!",
        "🌧️ A single raindrop can contain up to 1 million bacteria!",
        "🦋 Monarch butterflies migrate up to 3,000 miles - that's like flying from New York to California!"
    ]
    
    import random
    fact = random.choice(facts)
    
    return {
        'content': f"Here's an amazing eco-fact for you!\n\n{fact}\n\nWant to learn more? Take our environmental quizzes! 📚",
        'intent': 'eco_facts',
        'suggestions': ['Another fact', 'Related quiz', 'Eco tasks']
    }

def search_knowledge_base(message):
    """Search the knowledge base for relevant responses"""
    # Simple keyword matching
    kb_entries = BotKnowledgeBase.objects.filter(is_active=True)
    
    for entry in kb_entries:
        for keyword in entry.keywords:
            if keyword.lower() in message:
                entry.usage_count += 1
                entry.save()
                
                return {
                    'content': entry.answer,
                    'intent': entry.content_type,
                    'confidence': 0.9
                }
    
    return None

@login_required
@require_POST
def submit_feedback(request):
    """Submit feedback on bot response"""
    data = json.loads(request.body)
    message_id = data.get('message_id')
    feedback_type = data.get('feedback_type')
    rating = data.get('rating')
    comment = data.get('comment', '')
    
    try:
        message = ChatMessage.objects.get(id=message_id, message_type='bot')
        
        UserFeedback.objects.create(
            user=request.user,
            message=message,
            feedback_type=feedback_type,
            rating=rating,
            comment=comment
        )
        
        return JsonResponse({'success': True})
    except ChatMessage.DoesNotExist:
        return JsonResponse({'error': 'Message not found'}, status=404)

@login_required
def new_session(request):
    """Start a new chat session"""
    # Deactivate current session
    ChatSession.objects.filter(user=request.user, is_active=True).update(is_active=False)
    
    # Create new session
    new_session = ChatSession.objects.create(
        user=request.user,
        session_id=str(uuid.uuid4())
    )
    
    return JsonResponse({'session_id': new_session.session_id})
