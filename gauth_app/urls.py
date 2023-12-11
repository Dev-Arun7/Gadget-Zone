from django.urls import path
from gauth_app import views

urlpatterns = [
    path('signup/',views.user_signup,name='user_signup'),
    path('login/',views.user_login,name='user_login'),
    path('logout/',views.user_logout,name='user_logout'),
    path('profile/',views.profile,name='profile'),
    path('address/',views.address,name='address'),
    path('add_address/',views.add_address,name='add_address'),
    path('update_address/<int:id>',views.update_address,name='update_address'),
    path('delete_address/<int:id>/',views.delete_address,name='delete_address'),
   

]

