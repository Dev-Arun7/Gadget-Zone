from django.urls import path,include
from dashboard_app import views

urlpatterns = [
    path('',views.home,name='home'),
    path('main_category/',views.main_category,name='main_category'),
    path('add_main_category/',views.add_main_category,name='add_main_category'),
    path('update_main_category/<id>',views.update_main_category,name='update_main_category'),
    path('delete_main_category<id>/',views.delete_main_category,name='delete_main_category'),  
]  