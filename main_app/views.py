from django.shortcuts import render, redirect
from main_app.models import Main_Category, Product
from gauth_app.models import Cart, Wishlist, Address, Order
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.db.models import Q
from django.contrib import messages


def home(request):
    
    return render(request, "main/home.html")


def product_list(request):
    products = Product.objects.filter(deleted=False)
    return render(request, "main/product_list.html",{"data": products})


def category_products(request,id):
    main_category = Main_Category.objects.get(pk=id)
    products = Product.objects.filter(main_category=main_category, deleted=False)
    for product in products:
        product.offer_price = int(product.price * (1 - product.offer / 100))
    return render(request, "main/product_list.html", {'data': products})


def single_product(request, id):
    product = get_object_or_404(Product, id=id)
    similar_products = Product.objects.filter(main_category_id=product.main_category_id, deleted=False).exclude(id=id)
    
    # Fetch additional images from the related ProductImage model
    additional_images = product.additional_images.all()

    context = {
        "product": product,
        "products": similar_products,
        "additional_images": additional_images,
    }
    return render(request, "main/single_product.html", context)


def main_categories(request):
    return render(request,'main/main_categories.html')


###############################################################################################################
                        # Sorting and showing products on page #
###############################################################################################################


def product_search(request):
    query = request.GET.get('q', '')

    if query:
        query_parts = query.split(' ')
        # if user provide more than two words it splits and check both model name or brand name
        if len(query_parts) > 1:
            results = Product.objects.filter(
                Q(brand__icontains=query_parts[0]) & Q(model__icontains=query_parts[1])
            )
            # if the user provide only one word as a keyword search both field separately using OR
        else:
            results = Product.objects.filter(
                Q(model__icontains=query) | Q(brand__icontains=query)
            )
    else:
        results = Product.objects.all()

    return render(request, 'main/product_list.html', {'data': results, 'query': query})



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


def cart(request):
    raw_carts = Cart.objects.filter(user=request.user)

    # Loop through each item in the cart
    for item in raw_carts:
        if item.quantity > item.product.stock:
            item.delete()

    cart_items = Cart.objects.filter(user=request.user)
    subtotal = 0
    for item in cart_items: 
        subtotal = subtotal + item.product.offer_price * item.quantity

    context = {'cart': cart_items, 'subtotal': subtotal}
    return render(request, "main/cart.html", context)



def add_to_cart(request, product_id):
    # This function is responsible for adding a product to the user's cart.

    # Check if the request method is POST.
    if request.method == 'POST':
        # Check if the user is authenticated.
        if request.user.is_authenticated:
            # Get the product ID from the request.
            prod_id = int(request.POST.get('product_id'))

            # Retrieve the product from the database based on the product ID.
            product_check = Product.objects.get(id=prod_id)

            # Check if the product exists.
            if product_check:
                # Check if the product is already in the user's cart.
                if Cart.objects.filter(user=request.user.id, product_id=prod_id):
                    return JsonResponse({'status': "Product Already in cart..!"})
                else: 
                    # Create a new Cart object for the user and add the product.
                    Cart.objects.create(user=request.user, product_id=prod_id, quantity=1, total=product_check.offer_price)
                    return JsonResponse({'status': "Product added successfully"})
        else:
            return JsonResponse({'status': "Login to continue"})

    # If the request method is not POST, redirect to the home page.
    return redirect('/')



def update_cart(request):
    if request.method == 'POST':
        prod_id = int(request.POST.get('product_id'))
        if(Cart.objects.filter(user=request.user, product_id = prod_id)):
            prod_qty = int(request.POST.get('product_qty'))
            cart_data = Cart.objects.get(product_id=prod_id, user=request.user)
            cart_data.quantity = prod_qty
            cart_data.total = prod_qty * cart_data.product.offer_price
            cart_data.save()
            return JsonResponse({'status':"Updated Successfully"})
    return redirect('/')  


def delete_cart(request):
    if request.method == 'POST':
        prod_id = int(request.POST.get('product_id'))
        if(Cart.objects.filter(user = request.user, product_id=prod_id)):
            cartitem = Cart.objects.get(product_id=prod_id, user=request.user)
            cartitem.delete()
        return JsonResponse({'status':"Deleted Successfully"})
    return redirect('/')


def checkout(request):
    cart_items = Cart.objects.filter(user=request.user)
    addresses = Address.objects.filter(user=request.user)
    subtotal = 0
    for item in cart_items:
        subtotal = subtotal +item.product.offer_price * item.quantity

    context = {'subtotal': subtotal,
               'addresses': addresses,
               }

    return render(request, "main/checkout.html", context)


def orders(request):
    user = request.user
    cart_items = Cart.objects.filter(user=user)
    total_amount = sum(item.total for item in cart_items)

    if request.method == 'POST':
        address_id = request.POST.get('address_id')
        payment_type = request.POST.get('payment_type')

        # Create an order
        order = Order.objects.create(
            user=user,
            address_id=address_id,
            amount=total_amount,
            payment_type=payment_type,
            status='pending',
        )

        # Copy cart items to order
        for item in cart_items:
            order_items = order.orderitem_set.create(
                product=item.product,
                quantity=item.quantity,
                image=item.image,
            )

        # Clear the cart
        cart_items.delete()
        messages.success(request, 'Order placed successfully')

        return redirect('main/success.html')

    return render(request, 'main/orders.html')


def base(request):
    return render(request,'main/base.html')

def temp(request):
    return render(request,'main/temparary.html')


