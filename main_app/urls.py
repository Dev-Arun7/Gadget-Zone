from django.urls import path
from main_app import views

urlpatterns = [
    path('',views.home,name='home'),
    path('search/', views.product_search, name='product_search'),
    path('sort/',views.sort,name='sort'),

    path('product_list/',views.product_list,name='product_list'),
    path('single_product/<int:id>/<int:variant_id>/',views.single_product,name='single_product'),
    path('category_products/<int:id>/', views.category_products, name='category_products'),
    path('brand_products/<int:id>/', views.brand_products, name='brand_products'),

    path('main_categories/',views.main_categories,name='main_categories'),

    path('cart/',views.cart,name='cart'),
    path('add_to_cart/<int:product_id>/<int:variant_id>/', views.add_to_cart, name='add_to_cart'),
    path('update_cart/', views.update_cart, name='update_cart'),
    path('delete_cart/<int:product_id>/',views.delete_cart, name="delete_cart"),

    path('wishlist/', views.wishlist, name='wishlist'),
    path('add_to_wish/<int:product_id>/<int:variant_id>/', views.add_to_wish, name='add_to_wish'),
    path('delete_wish/<int:product_id>/',views.delete_wish, name="delete_wish"),


    path('checkout/',views.checkout,name='checkout'),  
    path('orders/',views.orders,name='orders'),  
    path('order_detail/<int:id>/',views.order_detail,name='order_detail'),  
    path('place_order/',views.place_order,name='place_order'),  
    path('cancel/<int:order_id>/', views.cancel, name='cancel'),


    
    path('base/',views.base,name='base'),
]
