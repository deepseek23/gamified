from django.urls import path
from . import views

app_name = 'rewards'

urlpatterns = [
    path('', views.token_dashboard, name='dashboard'),
    path('store/', views.reward_store, name='store'),
    path('purchase/<int:reward_id>/', views.purchase_reward, name='purchase'),
    path('my-rewards/', views.my_rewards, name='my_rewards'),
    path('transactions/', views.transaction_history, name='transactions'),
]
