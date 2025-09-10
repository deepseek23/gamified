from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from django.utils import timezone
from datetime import date
from .models import (
    EcoTokenTransaction, RewardItem, UserReward, 
    TokenEarningRule, DailyTokenLimit
)
from accounts.models import User

@login_required
def token_dashboard(request):
    """Display user's token balance and recent transactions"""
    recent_transactions = EcoTokenTransaction.objects.filter(
        user=request.user
    ).order_by('-created_at')[:10]
    
    # Get daily earning stats
    today = date.today()
    daily_limit, created = DailyTokenLimit.objects.get_or_create(
        user=request.user,
        date=today,
        defaults={'max_daily_tokens': 100}
    )
    
    context = {
        'user': request.user,
        'recent_transactions': recent_transactions,
        'daily_limit': daily_limit,
        'tokens_remaining_today': daily_limit.max_daily_tokens - daily_limit.tokens_earned_today,
    }
    return render(request, 'rewards/dashboard.html', context)

@login_required
def reward_store(request):
    """Display available rewards for purchase"""
    rewards = RewardItem.objects.filter(is_active=True)
    
    # Filter by user's school type if restriction exists
    if request.user.school_type:
        rewards = rewards.filter(
            models.Q(school_type_restriction='') | 
            models.Q(school_type_restriction=request.user.school_type)
        )
    
    # Add availability info for each reward
    reward_info = []
    for reward in rewards:
        can_purchase, message = reward.can_user_purchase(request.user)
        reward_info.append({
            'reward': reward,
            'can_purchase': can_purchase,
            'message': message
        })
    
    context = {
        'reward_info': reward_info,
        'user_tokens': request.user.total_eco_tokens,
    }
    return render(request, 'rewards/store.html', context)

@login_required
def purchase_reward(request, reward_id):
    """Purchase a reward item"""
    reward = get_object_or_404(RewardItem, id=reward_id, is_active=True)
    
    if request.method == 'POST':
        can_purchase, message = reward.can_user_purchase(request.user)
        
        if not can_purchase:
            messages.error(request, f"Cannot purchase: {message}")
            return redirect('rewards:store')
        
        # Process purchase
        with transaction.atomic():
            # Deduct tokens
            request.user.total_eco_tokens -= reward.cost_tokens
            request.user.save()
            
            # Create transaction record
            EcoTokenTransaction.objects.create(
                user=request.user,
                transaction_type='spent',
                amount=-reward.cost_tokens,
                description=f"Purchased {reward.name}",
                balance_after=request.user.total_eco_tokens
            )
            
            # Create user reward record
            user_reward = UserReward.objects.create(
                user=request.user,
                reward_item=reward,
                tokens_spent=reward.cost_tokens
            )
            
            # Update stock if limited
            if reward.stock_quantity is not None:
                reward.stock_quantity -= 1
                reward.save()
        
        messages.success(request, f"Successfully purchased {reward.name}!")
        return redirect('rewards:my_rewards')
    
    context = {
        'reward': reward,
        'can_purchase': reward.can_user_purchase(request.user)[0],
        'message': reward.can_user_purchase(request.user)[1],
    }
    return render(request, 'rewards/purchase_confirm.html', context)

@login_required
def my_rewards(request):
    """Display user's purchased rewards"""
    user_rewards = UserReward.objects.filter(
        user=request.user
    ).select_related('reward_item').order_by('-purchased_at')
    
    context = {
        'user_rewards': user_rewards,
    }
    return render(request, 'rewards/my_rewards.html', context)

@login_required
def transaction_history(request):
    """Display complete transaction history"""
    transactions = EcoTokenTransaction.objects.filter(
        user=request.user
    ).order_by('-created_at')
    
    # Pagination could be added here
    context = {
        'transactions': transactions,
    }
    return render(request, 'rewards/transaction_history.html', context)

def award_tokens(user, source, amount, description="", **kwargs):
    """
    Utility function to award tokens to a user
    This should be called from other apps when users complete activities
    """
    # Check daily limit
    today = date.today()
    daily_limit, created = DailyTokenLimit.objects.get_or_create(
        user=user,
        date=today,
        defaults={'max_daily_tokens': 100}
    )
    
    if not daily_limit.can_earn_tokens(amount):
        return False, "Daily token limit reached"
    
    # Get earning rule for this activity
    try:
        rule = TokenEarningRule.objects.get(activity=source, is_active=True)
        # Calculate actual tokens based on rules
        streak_days = kwargs.get('streak_days', 0)
        calculated_amount = rule.calculate_tokens(user, streak_days)
        amount = min(amount, calculated_amount)  # Use the lower amount
    except TokenEarningRule.DoesNotExist:
        pass  # Use the provided amount
    
    # Award tokens
    with transaction.atomic():
        user.total_eco_tokens += amount
        user.save()
        
        # Create transaction record
        EcoTokenTransaction.objects.create(
            user=user,
            transaction_type='earned',
            source=source,
            amount=amount,
            description=description,
            balance_after=user.total_eco_tokens,
            **{k: v for k, v in kwargs.items() if k in ['quiz_id', 'task_id', 'achievement_id']}
        )
        
        # Update daily limit
        daily_limit.add_tokens(amount)
    
    return True, f"Earned {amount} eco-tokens!"
