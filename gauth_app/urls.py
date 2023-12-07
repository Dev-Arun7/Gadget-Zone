from django.urls import path
from gauth_app import views

urlpatterns = [
    path('signup/',views.user_signup,name='user_signup'),
    path('login/',views.user_login,name='user_login'),
]