from django.shortcuts import render, redirect
from main_app.models import Main_Category, Product
from gauth_app.models import Cart, Wishlist
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404


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



###############################################################################################################
                            # Cart and Wishlist #
###############################################################################################################




def add_to_cart(request, product_id):
    # Retrieve the product
    product = get_object_or_404(Product, id=product_id)

    # Check if the user is authenticated
    if request.user.is_authenticated:
        # Check if the product is already in the user's cart
        cart_item, created = Cart.objects.get_or_create(user=request.user, product=product)

        # If the product is already in the cart, increase the quantity
        if not created:
            cart_item.quantity += 1
        else:
            # If it's a new product in the cart, set the quantity to 1
            cart_item.quantity = 1

        cart_item.save()

        # Return a JSON response indicating success
        return JsonResponse({'status': 'success', 'message': 'Item added to cart successfully!'})
    else:
        # Return a JSON response indicating the need for authentication
        return JsonResponse({'status': 'error', 'message': 'User not authenticated'})
    


    
def cart(request):
    cart_items = Cart.objects.all()

    # Create a list to store product details for each item in the cart
    cart_data = []

    # Loop through each item in the cart
    for item in cart_items:
        # Get the associated product for the current cart item
        print(f"Product ID: {item.product_id}, Image: {item.image}")
        product = item.product
        discounted_price = product.price - (product.price * (product.offer / 100))
        total = discounted_price * item.quantity

        # Append a dictionary with product details to the cart_data list
        cart_data.append({
            'product_name': product.model,  
            'product_brand': product.brand, 
            'product_price': discounted_price,
            'product_offer': product.offer,  
            'quantity': item.quantity,
            'total': total,
            'image': product.image,
        })

    return render(request, "main/cart.html", {"cart_data": cart_data})



def update_cart_quantity(request):
    if request.method == 'POST':
        product_id = request.POST.get('product_id')
        quantity = request.POST.get('quantity')

        # Update the cart item with the new quantity
        cart_item = Cart.objects.get(product_id=product_id)
        cart_item.quantity = quantity
        cart_item.save()

        # Calculate the new total for the cart item
        discounted_price = cart_item.product.price - (cart_item.product.price * (cart_item.product.offer / 100))
        cart_item.total = discounted_price * cart_item.quantity
        cart_item.save()

        # Return the updated total for the cart item
        return JsonResponse({'total': cart_item.total})




def base(request):
    return render(request,'main/base.html')

def temp(request):
    return render(request,'main/temparary.html')


