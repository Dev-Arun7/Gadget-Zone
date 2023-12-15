from django.urls import path
from main_app import views

app_name = 'main_app'

urlpatterns = [
    path('',views.home,name='home'),
    path('product_list/',views.product_list,name='product_list'),
    path('single_product/<int:id>/',views.single_product,name='single_product'),
    path('all_featurephones/',views.all_featutephones,name='all_featurephones'),
    path('all_smartphones/',views.all_smartphones,name='all_smartphones'),
    path('category_products/<int:id>/', views.category_products, name='category_products'),
    path('main_categories/',views.main_categories,name='main_categories'),
    path('base/',views.base,name='base'),
    path('update_item/',views.updateItem,name='update_item'),



]


