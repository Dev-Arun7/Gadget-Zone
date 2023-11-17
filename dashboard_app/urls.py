from django.urls import path,include
from dashboard_app import views

urlpatterns = [
    path('',views.home,name='home'),
    path('main_category/',views.main_category,name='home'),
    
]  