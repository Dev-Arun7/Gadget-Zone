from django.urls import path
from dashboard_app import views

urlpatterns = [
    path('',views.dashboard_home,name='dashboard_home'),
    path('login/',views.dashboard_login,name='dashboard_login'),
    path('logout/',views.dashboard_logout,name='dashboard_logout'),

    path('main_category/',views.main_category,name='main_category'),
    path('add_main_category/',views.add_main_category,name='add_main_category'),

    path('update_main_category/<int:id>/', views.update_main_category, name='update_main_category'),
    path('soft_delete_category/<int:id>/',views.soft_delete_category,name='soft_delete_category'), 
    path('delete_main_category/<int:id>/',views.delete_main_category,name='delete_main_category'), 

    path('brands/',views.brands,name='brands'),
    path('add_brand/',views.add_brand,name='add_brand'),
    path('update_brand/<int:id>/',views.update_brand,name='update_brand'),
    path('delete_brand/<int:id>/',views.delete_brand,name='delete_brand'),

    path('products/',views.products,name='products'),
    path('all_products/',views.all_products,name='all_products'),
    path('add_product/',views.add_product,name='add_product'), 
    path('update_product/<int:id>/',views.update_product,name='update_product'),
    path('delete_product/<int:id>/',views.delete_product,name='delete_product'),  

    path('add_variant/<int:id>/',views.add_variant,name='add_variant'), 
    path('update_variant/<int:id>/',views.update_variant,name='update_variant'), 
    path('soft_delete_product/<int:id>/',views.soft_delete_product,name='soft_delete_product'), 
    
    path('orders/',views.orders,name='orders'), 
    path('update_order_status/<int:order_id>/', views.update_order_status, name='update_order_status'),

    path('users/',views.users,name='users'),
]  