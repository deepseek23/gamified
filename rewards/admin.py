from django.contrib import admin
from .models import EcoTokenTransaction, RewardItem, UserReward, TokenEarningRule, DailyTokenLimit

@admin.register(EcoTokenTransaction)
class EcoTokenTransactionAdmin(admin.ModelAdmin):
    list_display = ('user', 'transaction_type', 'source', 'amount', 'balance_after', 'created_at')
    list_filter = ('transaction_type', 'source', 'created_at')
    search_fields = ('user__username', 'description')
    readonly_fields = ('balance_after', 'created_at')
    ordering = ['-created_at']

@admin.register(RewardItem)
class RewardItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'item_type', 'cost_tokens', 'is_active', 'stock_quantity', 'min_level_required')
    list_filter = ('item_type', 'is_active', 'min_level_required', 'school_type_restriction')
    search_fields = ('name', 'description')
    list_editable = ('is_active', 'cost_tokens')

@admin.register(UserReward)
class UserRewardAdmin(admin.ModelAdmin):
    list_display = ('user', 'reward_item', 'tokens_spent', 'status', 'purchased_at')
    list_filter = ('status', 'purchased_at', 'reward_item__item_type')
    search_fields = ('user__username', 'reward_item__name')
    readonly_fields = ('purchased_at',)

@admin.register(TokenEarningRule)
class TokenEarningRuleAdmin(admin.ModelAdmin):
    list_display = ('activity', 'base_tokens', 'bonus_multiplier', 'streak_required', 'level_multiplier', 'is_active')
    list_filter = ('is_active', 'level_multiplier')
    list_editable = ('base_tokens', 'bonus_multiplier', 'is_active')

@admin.register(DailyTokenLimit)
class DailyTokenLimitAdmin(admin.ModelAdmin):
    list_display = ('user', 'date', 'tokens_earned_today', 'max_daily_tokens')
    list_filter = ('date',)
    search_fields = ('user__username',)
