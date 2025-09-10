from django.contrib import admin
from .models import (
    LeaderboardType, LeaderboardEntry, GlobalLeaderboard, LocalLeaderboard,
    LeaderboardReward, UserLeaderboardReward, LeaderboardSeason, SeasonParticipant
)

@admin.register(LeaderboardType)
class LeaderboardTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'scope', 'period', 'metric', 'is_active', 'max_entries')
    list_filter = ('scope', 'period', 'metric', 'is_active')
    search_fields = ('name', 'description')
    list_editable = ('is_active',)

@admin.register(LeaderboardEntry)
class LeaderboardEntryAdmin(admin.ModelAdmin):
    list_display = ('leaderboard_type', 'user', 'rank', 'score', 'get_rank_change_display', 'updated_at')
    list_filter = ('leaderboard_type__scope', 'leaderboard_type__period', 'updated_at')
    search_fields = ('user__username', 'leaderboard_type__name')
    readonly_fields = ('created_at', 'updated_at')

@admin.register(GlobalLeaderboard)
class GlobalLeaderboardAdmin(admin.ModelAdmin):
    list_display = ('user', 'global_rank', 'total_score', 'total_achievements', 'last_updated')
    search_fields = ('user__username',)
    readonly_fields = ('last_updated',)
    ordering = ['global_rank']

@admin.register(LocalLeaderboard)
class LocalLeaderboardAdmin(admin.ModelAdmin):
    list_display = ('location_type', 'location_value', 'user', 'rank', 'score', 'period_type')
    list_filter = ('location_type', 'period_type', 'last_updated')
    search_fields = ('user__username', 'location_value')

@admin.register(LeaderboardReward)
class LeaderboardRewardAdmin(admin.ModelAdmin):
    list_display = ('leaderboard_type', 'rank_range', 'token_reward', 'experience_reward', 'is_active')
    list_filter = ('leaderboard_type__scope', 'is_active')
    
    def rank_range(self, obj):
        if obj.min_rank == obj.max_rank:
            return f"#{obj.min_rank}"
        return f"#{obj.min_rank}-{obj.max_rank}"
    rank_range.short_description = "Rank Range"

@admin.register(UserLeaderboardReward)
class UserLeaderboardRewardAdmin(admin.ModelAdmin):
    list_display = ('user', 'leaderboard_reward', 'tokens_awarded', 'experience_awarded', 'awarded_at')
    list_filter = ('awarded_at', 'leaderboard_reward__leaderboard_type')
    search_fields = ('user__username',)

@admin.register(LeaderboardSeason)
class LeaderboardSeasonAdmin(admin.ModelAdmin):
    list_display = ('name', 'season_type', 'start_date', 'end_date', 'is_active', 'get_participants_count')
    list_filter = ('season_type', 'is_active', 'start_date')
    search_fields = ('name', 'description')
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'description', 'season_type')
        }),
        ('Timing', {
            'fields': ('start_date', 'end_date')
        }),
        ('Rules', {
            'fields': ('bonus_multiplier', 'featured_activities')
        }),
        ('Rewards', {
            'fields': ('winner_tokens', 'winner_badge', 'participation_tokens')
        }),
        ('Display', {
            'fields': ('theme_color', 'banner_image', 'is_active')
        }),
    )

@admin.register(SeasonParticipant)
class SeasonParticipantAdmin(admin.ModelAdmin):
    list_display = ('user', 'season', 'season_rank', 'season_score', 'rewards_claimed', 'joined_at')
    list_filter = ('season', 'rewards_claimed', 'joined_at')
    search_fields = ('user__username', 'season__name')
    readonly_fields = ('joined_at', 'last_activity')
