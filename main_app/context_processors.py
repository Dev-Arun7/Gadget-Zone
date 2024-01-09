from main_app.models import Main_Category, Product

def extras(request):
    main_category = Main_Category.objects.filter(deleted=False)
    products = Product.objects.filter(deleted=False)
    customer = request.user
    for product in products:
        product.offer_price = int(product.price * (1 - product.offer / 100))
    
    context = {'default_main_category' : main_category,
                'default_product': products,
                'customer':customer
                }
    return context