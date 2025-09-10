from django.urls import path
from . import views

app_name = 'chatbot'

urlpatterns = [
    path('', views.chat_interface, name='chat'),
    path('send/', views.send_message, name='send_message'),
    path('feedback/', views.submit_feedback, name='submit_feedback'),
    path('new-session/', views.new_session, name='new_session'),
]
