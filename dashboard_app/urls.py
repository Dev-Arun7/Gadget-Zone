from django.urls import path
from dashboard_app import views

urlpatterns = [
    path('',views.dashboard_home,name='dashboard_home'),
    path('login/',views.dashboard_login,name='dashboard_login'),
    path('logout/',views.dashboard_logout,name='dashboard_logout'),
    path('main_category/',views.main_category,name='main_category'),
    path('add_main_category/',views.add_main_category,name='add_main_category'),
    path('update_main_category/<int:id>/', views.update_main_category, name='update_main_category'),
    path('delete_main_category/<int:id>/',views.delete_main_category,name='delete_main_category'), 

    path('all_products/',views.all_products,name='all_products'),
    path('add_product/',views.add_product,name='add_product'), 
    path('update_product/<int:id>/',views.update_product,name='update_product'), 
    path('delete_product/<int:id>/',views.delete_product,name='delete_product'), 

    path('users/',views.users,name='users'),
]  