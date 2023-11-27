from main_app.models import Main_Category, Product

def extras(request):
    main_category = Main_Category.objects.all()
    product = Product.objects.all()
    context = {'default_main_category' : main_category, 'default_product': product}
    return context