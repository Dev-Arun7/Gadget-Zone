from django.urls import path,include
from dashboard_app import views

urlpatterns = [
    path('',views.home,name='home'),
    path('all_products',views.all_products,name='home'),
]