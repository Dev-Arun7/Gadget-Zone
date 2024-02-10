from main_app.models import Main_Category, Product, Brand
from gauth_app.models import Cart

def extras(request):
    main_category = Main_Category.objects.filter(deleted=False)
    products = Product.objects.all()
    brands = Brand.objects.all()
    customer = request.user
    cart_count = Cart.objects.all().count()
    
    context = {'default_main_category' : main_category,
                'default_product': products,
                'customer':customer,
                'brands': brands,
                'cart_count': cart_count,
                }
    return context