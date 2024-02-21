from main_app.models import Main_Category, Product, Brand, ProductVariant
from gauth_app.models import Cart, Wishlist, Customer
from django.contrib.auth.models import AnonymousUser

def extras(request):
    main_category = Main_Category.objects.filter(deleted=False).order_by('?')
    products = ProductVariant.objects.filter(deleted=False).order_by('-id')
    brands = Brand.objects.all().order_by('?')
    
    # Check if the user is authenticated
    if isinstance(request.user, AnonymousUser):
        cart_count = 0
        wishlist_count = 0
    else:
        cart_count = Cart.objects.filter(user=request.user).count()
        wishlist_count = Wishlist.objects.filter(user=request.user).count()

    context = {
        'default_main_category': main_category,
        'default_product': products,
        'customer': request.user,
        'brands': brands,
        'cart_count': cart_count,
        'wishlist_count': wishlist_count,
        'products': products,
    }
    return context