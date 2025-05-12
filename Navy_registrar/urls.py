from django.urls import path
from . import views

app_name = 'Navy_registrar'

urlpatterns = [
    path('register/', views.register, name='register'),
    path('', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('chatbot/', views.chatbot, name='chatbot'),
]