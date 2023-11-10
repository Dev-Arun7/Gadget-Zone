from django.urls import path,include
from main_app import views

urlpatterns = [
    path('',views.home,name='home'),
    path('all_products',views.home,name='home'),
]