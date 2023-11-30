from django.shortcuts import render
from django.http import HttpResponse  
from main_app.models import Main_Category, Product


def home(request):
    return render(request, "main/home.html")


def product_list(request):
    products = Product.objects.filter(deleted=False)
    for product in products:
        product.offer_price = int(product.price * (1 - product.offer / 100))
    return render(request, "main/product_list.html",{"data": products})

def category_products(request,id):
    main_category = Main_Category.objects.get(pk=id)
    products = Product.objects.filter(main_category=main_category, deleted=False)
    for product in products:
        product.offer_price = int(product.price * (1 - product.offer / 100))
    return render(request, "main/product_list.html", {'data': products})

def single_product(request, id):
    product = Product.objects.get(id=id)
    similar_products = Product.objects.filter(main_category_id=product.main_category_id, deleted=False).exclude(id=id)
    offer_price = int(product.price * (1 - product.offer / 100))
    context = {
        "product": product,
        "offer_price": offer_price,
        "products": similar_products,
    }
    return render(request, "main/single_product.html", context)

def main_categories(request):
    return render(request,'main/main_categories.html')



###############################################################################################################
                        # Sorting and showing products on page #
###############################################################################################################

def all_featutephones(request):
    # Get the Main_Category named 'Featurephone'
    featurephone_category = Main_Category.objects.get(name='Feature Phones')

    # Get all products related to the 'Featurephone' category
    featurephone_products = Product.objects.filter(main_category=featurephone_category)
    for product in featurephone_products:
        product.offer_price = int(product.price * (1 - product.offer / 100))

    return render(request, 'main/product_list.html', {'data': featurephone_products})

def all_smartphones(request):
    # Get the Main_Category named 'Featurephone'
    smartphone_category = Main_Category.objects.get(name='Smartphones')

    # Get all products related to the 'Featurephone' category
    smartphones_products = Product.objects.filter(main_category=smartphone_category)
    for product in smartphones_products:
        product.offer_price = int(product.price * (1 - product.offer / 100))

    return render(request, 'main/product_list.html', {'data': smartphones_products})


def budget_phones(request):
    # Filter products with prices less than 20000
    data = Product.objects.filter(price__lt=20000)

    # Calculate offer price for each product and add it to the data dictionary
    for product in data:
        product.offer_price = int(product.price * (1 - product.offer / 100))
    print("Debug - Budget Phones Data:", data) 
    return render(request, "main/product_list.html", {"budget": data})


def signup(request):
    return render(request,'main/signup.html')

def base(request):
    return render(request,'main/base.html')

def temp(request):
    return render(request,'main/temparary.html')


