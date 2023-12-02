from django.urls import path,include
from gauth_app import views

urlpatterns = [
    path('user_login/', views.user_login, name='user_login'),
    path('user_signup/', views.user_signup, name='user_signup'),
    path('user_logout/', views.user_logout, name='user_logout'),
]