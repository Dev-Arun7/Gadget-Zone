from django.urls import path
from main_app import views

urlpatterns = [
    path('',views.home,name='home'),
    path('all_products/',views.home,name='home'),
    path('signup/',views.signup,name='home'),
    path('base/',views.base,name='base'),
]
