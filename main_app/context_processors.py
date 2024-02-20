from main_app.models import Main_Category, Product, Brand, ProductVariant
from gauth_app.models import Cart, Wishlist

def extras(request):
    main_category = Main_Category.objects.filter(deleted=False).order_by('?')
    products = ProductVariant.objects.filter(deleted=False).order_by('-id')
    brands = Brand.objects.all().order_by('?')
    customer = request.user
    cart_count = Cart.objects.all().count()
    wishlist_count = Wishlist.objects.all().count()
    
    context = {'default_main_category' : main_category,
                'default_product': products,
                'customer':customer,
                'brands': brands,
                'cart_count': cart_count,
                'wishlist_count': wishlist_count,
                'products': products,
                }
    return context