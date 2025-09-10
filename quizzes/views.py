from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from django.utils import timezone
from django.http import JsonResponse, HttpResponseBadRequest
from django.views.decorators.http import require_POST
from django.urls import reverse
import json
import random

from .models import QuizCategory, Quiz, Question, Answer, QuizAttempt, UserAnswer
from rewards.views import award_tokens
from accounts.models import UserProfile


def quiz_categories(request):
    """Display all active quiz categories."""
    categories = QuizCategory.objects.filter(is_active=True).prefetch_related('quizzes')
    context = {'categories': categories}
    return render(request, 'quizzes/categories.html', context)


def quiz_list(request, category_id=None):
    """
    Display quizzes, optionally filtered by category.
    Includes quiz_progress when user is authenticated.
    """
    quizzes = Quiz.objects.filter(is_active=True).select_related('category')

    category = None
    if category_id:
        category = get_object_or_404(QuizCategory, id=category_id, is_active=True)
        quizzes = quizzes.filter(category=category)

    context = {'quizzes': quizzes, 'category': category}

    # Add user progress info if logged in
    if request.user.is_authenticated:
        user_attempts = QuizAttempt.objects.filter(
            user=request.user,
            is_completed=True
        ).values_list('quiz_id', flat=True)

        quiz_progress = []
        for quiz in quizzes:
            progress_info = {
                'quiz': quiz,
                'completed': quiz.id in user_attempts,
                # guard if user object doesn't have `level` attribute
                'can_access': getattr(request.user, 'level', 1) >= getattr(quiz, 'min_level_required', 1),
            }

            if quiz.id in user_attempts:
                best_attempt = QuizAttempt.objects.filter(
                    user=request.user,
                    quiz=quiz,
                    is_completed=True
                ).order_by('-score', 'time_taken_seconds').first()
                progress_info['best_score'] = best_attempt.score if best_attempt else 0

            quiz_progress.append(progress_info)

        context['quiz_progress'] = quiz_progress

    return render(request, 'quizzes/quiz_list.html', context)


@login_required
def quiz_detail(request, quiz_id):
    """Display quiz details and start button"""
    quiz = get_object_or_404(Quiz, id=quiz_id, is_active=True)
    
    # Check if user can access this quiz
    if quiz.min_level_required > request.user.level:
        messages.error(request, f"You need to reach level {quiz.min_level_required} to access this quiz.")
        return redirect('quizzes:list')
    
    # Get user's previous attempts
    user_attempts = QuizAttempt.objects.filter(
        user=request.user, 
        quiz=quiz
    ).order_by('-started_at')
    
    best_attempt = user_attempts.filter(is_completed=True).order_by('-score').first()
    
    # 👇 Add can_start flag
    can_start = quiz.min_level_required <= request.user.level
    
    context = {
        'quiz': quiz,
        'user_attempts': user_attempts[:5],  # Show last 5 attempts
        'best_attempt': best_attempt,
        'questions_count': quiz.get_questions_count(),
        'can_start': can_start,   # 👈 important
    }
    return render(request, 'quizzes/quiz_detail.html', context)



@login_required
def start_quiz(request, quiz_id):
    """Start a new quiz attempt and redirect to take_quiz."""
    quiz = get_object_or_404(Quiz, id=quiz_id, is_active=True)

    # Check access
    if getattr(quiz, 'min_level_required', 1) > getattr(request.user, 'level', 1):
        messages.error(request, "You don't have access to this quiz.")
        return redirect(reverse('quizzes:detail', kwargs={'quiz_id': quiz_id}))

    # Create new attempt
    attempt = QuizAttempt.objects.create(
        user=request.user,
        quiz=quiz,
        total_questions=quiz.get_questions_count() if hasattr(quiz, 'get_questions_count') else quiz.questions.count(),
        started_at=timezone.now()
    )

    return redirect(reverse('quizzes:take_quiz', kwargs={'attempt_id': attempt.id}))


@login_required
def take_quiz(request, attempt_id):
    """Render the quiz-taking page with questions and already answered state."""
    attempt = get_object_or_404(
        QuizAttempt,
        id=attempt_id,
        user=request.user,
        is_completed=False
    )

    # Load questions related to the quiz
    # Assumes Quiz model has related_name 'questions'
    questions_qs = attempt.quiz.questions.prefetch_related('answers').all()
    questions = list(questions_qs)

    if getattr(attempt.quiz, 'randomize_questions', False):
        random.shuffle(questions)

    # Already answered question IDs
    answered_questions = UserAnswer.objects.filter(attempt=attempt).values_list('question_id', flat=True)

    context = {
        'attempt': attempt,
        'questions': questions,
        'answered_questions': list(answered_questions),
        'current_question_index': len(answered_questions),
        'total_questions': len(questions),
    }
    return render(request, 'quizzes/take_quiz.html', context)


@login_required
@require_POST
def submit_answer(request, attempt_id):
    """
    Submit an answer for a question.
    Expects JSON body with keys: question_id, answer_id (optional), text_answer (optional).
    Returns JSON: { is_correct, is_complete, explanation?, redirect_url? }
    """
    attempt = get_object_or_404(
        QuizAttempt,
        id=attempt_id,
        user=request.user,
        is_completed=False
    )

    # Parse JSON safely
    try:
        data = json.loads(request.body.decode('utf-8'))
    except (ValueError, json.JSONDecodeError):
        return HttpResponseBadRequest('Invalid JSON')

    question_id = data.get('question_id')
    answer_id = data.get('answer_id')
    text_answer = data.get('text_answer', '')

    if not question_id:
        return JsonResponse({'error': 'Missing question_id'}, status=400)

    question = get_object_or_404(Question, id=question_id, quiz=attempt.quiz)

    # Prevent duplicate answers (race-safe with transaction)
    if UserAnswer.objects.filter(attempt=attempt, question=question).exists():
        return JsonResponse({'error': 'Question already answered'}, status=400)

    selected_answer = None
    is_correct = False

    # Determine correctness depending on question type
    if question.question_type in ['multiple_choice', 'true_false']:
        if not answer_id:
            return JsonResponse({'error': 'Missing answer_id for this question'}, status=400)
        selected_answer = get_object_or_404(Answer, id=answer_id, question=question)
        is_correct = bool(selected_answer.is_correct)
    elif question.question_type == 'fill_blank':
        # assume question.get_correct_answer() returns an Answer-like object or text
        correct = None
        if hasattr(question, 'get_correct_answer'):
            correct = question.get_correct_answer()
        if correct:
            # support both Answer-like or plain text
            correct_text = getattr(correct, 'text', correct)
            is_correct = text_answer.lower().strip() == str(correct_text).lower().strip()
        else:
            # if no correct answer defined, treat as incorrect
            is_correct = False
    else:
        # fallback for other question types (mark incorrect)
        is_correct = False

    # Save answer and update attempt atomically
    with transaction.atomic():
        user_answer = UserAnswer.objects.create(
            attempt=attempt,
            question=question,
            selected_answer=selected_answer,
            text_answer=text_answer,
            is_correct=is_correct
        )

        if is_correct:
            # ensure field exists on model
            attempt.correct_answers = getattr(attempt, 'correct_answers', 0) + 1
            attempt.save(update_fields=['correct_answers'])

    # Check completion
    total_answered = UserAnswer.objects.filter(attempt=attempt).count()
    is_complete = total_answered >= (attempt.total_questions or (attempt.quiz.get_questions_count() if hasattr(attempt.quiz, 'get_questions_count') else attempt.quiz.questions.count()))

    response_data = {
        'is_correct': is_correct,
        'is_complete': is_complete,
        'explanation': question.explanation if getattr(attempt.quiz, 'show_correct_answers', False) else '',
    }

    if is_complete:
        # use reverse to build redirect URL
        response_data['redirect_url'] = reverse('quizzes:complete', kwargs={'attempt_id': attempt.id})

    return JsonResponse(response_data)


@login_required
def complete_quiz(request, attempt_id):
    """Finish attempt (if not already finished), award tokens/XP and present results."""
    attempt = get_object_or_404(QuizAttempt, id=attempt_id, user=request.user)

    if not attempt.is_completed:
        with transaction.atomic():
            # Ensure calculate_score exists; otherwise compute safe fallback
            if hasattr(attempt, 'calculate_score'):
                attempt.calculate_score()
            else:
                # fallback: compute percent using correct answers / total_questions
                correct = getattr(attempt, 'correct_answers', UserAnswer.objects.filter(attempt=attempt, is_correct=True).count())
                total = attempt.total_questions or (attempt.quiz.get_questions_count() if hasattr(attempt.quiz, 'get_questions_count') else attempt.quiz.questions.count())
                attempt.score = round((correct / total) * 100, 1) if total else 0

            attempt.is_completed = True
            attempt.completed_at = timezone.now()

            # Calculate time taken if started_at exists
            if getattr(attempt, 'started_at', None):
                time_taken = (attempt.completed_at - attempt.started_at).total_seconds()
                attempt.time_taken_seconds = int(time_taken)
            else:
                attempt.time_taken_seconds = getattr(attempt, 'time_taken_seconds', 0)

            # Award tokens/bonuses
            base_tokens = getattr(attempt.quiz, 'base_tokens_reward', 0)
            bonus_tokens = 0

            if hasattr(attempt, 'is_perfect_score') and attempt.is_perfect_score():
                bonus_tokens += getattr(attempt.quiz, 'perfect_score_bonus', 0)

            if hasattr(attempt, 'get_time_bonus_tokens'):
                try:
                    bonus_tokens += int(attempt.get_time_bonus_tokens())
                except Exception:
                    # if method exists but fails, ignore bonus
                    pass

            total_tokens = base_tokens + bonus_tokens
            attempt.tokens_earned = total_tokens
            attempt.experience_gained = total_tokens  # can be changed if desired

            attempt.save()

            # Try awarding tokens; if award_tokens fails, log message (award_tokens should handle exceptions)
            try:
                success, msg = award_tokens(
                    user=request.user,
                    source='quiz_completion',
                    amount=total_tokens,
                    description=f"Completed quiz: {attempt.quiz.title}",
                    quiz_id=attempt.quiz.id
                )
            except Exception:
                success, msg = False, 'Failed to award tokens'

            # Add experience to user (if method exists)
            leveled_up = False
            if hasattr(request.user, 'add_experience'):
                try:
                    leveled_up = request.user.add_experience(attempt.experience_gained)
                except Exception:
                    leveled_up = False

            # Update user profile safely
            profile, created = UserProfile.objects.get_or_create(user=request.user)
            profile.quizzes_completed = getattr(profile, 'quizzes_completed', 0) + 1
            profile.total_quiz_score = getattr(profile, 'total_quiz_score', 0) + getattr(attempt, 'score', 0)
            try:
                profile.average_quiz_score = profile.total_quiz_score / profile.quizzes_completed
            except Exception:
                profile.average_quiz_score = getattr(profile, 'average_quiz_score', 0)
            # update_streak might be optional
            if hasattr(profile, 'update_streak'):
                try:
                    profile.update_streak()
                except Exception:
                    pass
            profile.save()

            if leveled_up:
                messages.success(request, f"Congratulations! You leveled up to level {getattr(request.user, 'level', '?')}!")

    # Collect answers for review
    user_answers = UserAnswer.objects.filter(attempt=attempt).select_related('question', 'selected_answer').order_by('id')

    context = {
        'attempt': attempt,
        'user_answers': user_answers,
        'percentage_score': getattr(attempt, 'score', 0),
        'tokens_earned': getattr(attempt, 'tokens_earned', 0),
    }
    return render(request, 'quizzes/quiz_complete.html', context)


@login_required
def quiz_leaderboard(request, quiz_id):
    """Display leaderboard for a specific quiz."""
    quiz = get_object_or_404(Quiz, id=quiz_id, is_active=True)

    top_attempts = QuizAttempt.objects.filter(
        quiz=quiz,
        is_completed=True
    ).select_related('user').order_by('-score', 'time_taken_seconds')[:20]

    user_best = None
    if request.user.is_authenticated:
        user_best = QuizAttempt.objects.filter(
            quiz=quiz,
            user=request.user,
            is_completed=True
        ).order_by('-score', 'time_taken_seconds').first()

    context = {'quiz': quiz, 'top_attempts': top_attempts, 'user_best': user_best}
    return render(request, 'quizzes/leaderboard.html', context)
