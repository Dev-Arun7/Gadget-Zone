from main_app.models import Main_Category, Product

def extras(request):
    main_category = Main_Category.objects.filter(deleted=False)
    products = Product.objects.all()
    customer = request.user
    
    context = {'default_main_category' : main_category,
                'default_product': products,
                'customer':customer
                }
    return context