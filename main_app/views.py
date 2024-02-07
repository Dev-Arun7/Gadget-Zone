from django.shortcuts import render, redirect
from main_app.models import Main_Category, Product, ProductVariant
from gauth_app.models import Cart, Wishlist, Address, Order
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.db.models import Q
from django.contrib import messages
from django.db.models import Sum
from django.urls import reverse
import json
import random




def home(request):
    products = ProductVariant.objects.filter(deleted=False).order_by('id')
    context = {'products': products}  
    return render(request, "main/home.html", context)


def product_list(request):
    products = ProductVariant.objects.filter(deleted=False).order_by('-id')
    context = {'products': products}
    print(context)  
    return render(request, "main/product_list.html", context)


def category_products(request, id):
    # Retrieve the product variants associated with the selected main category
    product_variants = ProductVariant.objects.filter(product__main_category_id=id, deleted=False)

    # Pass the product variants to the template for rendering
    return render(request, "main/product_list.html", {'products': product_variants})



def single_product(request, id, variant_id):
    # Get the product and its variants
    product = get_object_or_404(Product, id=id)

    # Fetch the specific variant using the provided variant_id
    variant = get_object_or_404(ProductVariant, id=variant_id, product=product)

    variants = product.productvariant_set.all()  # Use the related name 'productvariant_set' to access variants

    # Fetch additional images from the related ProductImage model
    additional_images = product.additional_images.all()

    # Similar Products
    
    similar_products = ProductVariant.objects.filter(
    product__main_category=product.main_category
    ).exclude(id=variant.id).order_by('?')
    
    print(similar_products)
    context = {
        "product": product,
        "variants": variants,
        "variant": variant,
        "additional_images": additional_images,
        "similar_products": similar_products
    }
    return render(request, "main/single_product.html", context)


def main_categories(request):
    return render(request,'main/main_categories.html')


###############################################################################################################
                        # Sorting and showing products on page #
###############################################################################################################



def product_search(request):
    if request.method == "POST":
        searched = request.POST.get('searched')

        # Split the searched term into individual words
        search_terms = searched.split()

        # Initialize an empty Q object to build the query dynamically
        q_objects = Q()

        # Iterate through each search term and construct the query
        for term in search_terms:
            q_objects |= Q(product__model__icontains=term) | Q(product__brand__name__icontains=term)

        # Filter products based on the constructed query
        products = ProductVariant.objects.filter(q_objects).distinct()

        context = {
            'products': products,
        }
        return render(request, 'main/product_list.html', context)

    return redirect('main_app:home')


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



@login_required
def cart(request):
    # Retrieve all cart items along with related product and product variant details
    cart_items = Cart.objects.select_related('product', 'product_variant').filter(user=request.user).order_by('id')

    # Calculate subtotal for each item and total price for all items in the cart
    total_price = 0

    for item in cart_items:
        # Check if there is sufficient stock for the product variant
        if item.quantity <= item.product_variant.stock:
            # Calculate subtotal for the item
            item.subtotal = item.quantity * item.product_variant.offer_price
            # Add subtotal to the total price
            total_price += item.subtotal

    context = { 'cart': cart_items, 'subtotal': total_price }
    return render(request, 'main/cart.html', context)



def add_to_cart(request, product_id, variant_id):
    if request.method == 'POST':
        if request.user.is_authenticated:
            product = get_object_or_404(Product, id=product_id)
            variant = get_object_or_404(ProductVariant, id=variant_id)

            # Check if the product exists.
            if product:
                # Check if the product is already in the user's cart.
                if Cart.objects.filter(user=request.user, product=product, product_variant=variant).exists():
                    return JsonResponse({'status': "Product Already in cart..!", 'added': False})
                else: 
                    # Create a new Cart object for the user and add the product.
                    Cart.objects.create(user=request.user,
                                        product=product,
                                        product_variant=variant,
                                        quantity=1,
                                        total=variant.offer_price
                                        )
                    # Return success message
                    return JsonResponse({'status': "Product added successfully", 'added': True})
        else:
            return JsonResponse({'status': "Login to continue"})

    # If the request method is not POST, redirect to the home page.
    return redirect('main_app:home')




def update_cart(request):
    if request.method == 'POST':
        variant_id = int(request.POST.get('variant_id'))
        prod_qty = int(request.POST.get('product_qty'))  # Move this line outside the if condition to avoid scope issue
        
        # Retrieve the cart object based on user and product_variant_id
        cart = Cart.objects.get(user=request.user, product_variant_id=variant_id)
        
        # Update the quantity of the cart
        cart.quantity = prod_qty
        cart.total = cart.quantity * cart.product_variant.offer_price
        cart.save()  # Save the changes to the database
        
        return JsonResponse({'status': "Quantity updated", 'added': True})  # Return JSON response indicating success

    # If the request method is not POST, redirect to home
    return redirect('main_app:home')        









@login_required
def delete_cart(request, product_id):
    # Retrieve the cart item to delete
    cart_item = get_object_or_404(Cart, id=product_id)
    cart_item.delete()
    return redirect('main_app:cart') 


###############################################################################################################
                                # Checkout and Order #
###############################################################################################################


@login_required
def checkout(request):

    cart_items = Cart.objects.filter(quantity__gt=0, product_variant__stock__gt=0)
    addresses = Address.objects.filter(user=request.user)
    total_price = cart_items.aggregate(total_price=Sum('total'))['total_price'] or 0

    context = { 'subtotal': total_price,
               'addresses': addresses,
               }

    return render(request, "main/checkout.html", context)

@login_required
def orders(request):
    # Filter orders by the current user
    user_orders = Order.objects.filter(user=request.user).order_by('id')

    # Render the orders template with user's orders data
    return render(request, 'main/orders.html', {'orders': user_orders})


@login_required
def place_order(request):
    if request.method == 'POST':
        user = request.user
        address_id = request.POST.get('addressId')
        payment_type = request.POST.get('payment')  

        # Check if address is selected
        if not address_id:
            messages.error(request, "Please select an address.")
            return HttpResponseRedirect(reverse('main_app:checkout')) 
        
        if not payment_type:
            messages.error(request, "Please select payment method.")
            return HttpResponseRedirect(reverse('main_app:checkout'))
        
        cart_items = Cart.objects.filter(user=user, quantity__gt=0)
        in_stock_items = []
        out_of_stock_items = []

        for cart_item in cart_items:
            if cart_item.quantity <= cart_item.product_variant.stock:
                in_stock_items.append(cart_item)
            else:
                out_of_stock_items.append(cart_item)

        for cart_item in in_stock_items:
            order = Order.objects.create(
                user=user,
                address_id=address_id,
                product=cart_item.product,
                amount=cart_item.total,
                payment_type=payment_type, 
                status='pending',
                quantity=cart_item.quantity,
                image=cart_item.image,
                variant=cart_item.product_variant

            )
            cart_item.product_variant.stock -= cart_item.quantity
            cart_item.product_variant.save()
            cart_item.delete()

        if out_of_stock_items:
            messages.warning(request, "Some items are out of stock and were not included in the order.")

        return HttpResponseRedirect(reverse('main_app:home') + '?success=true')
    else:
        messages.error(request, "Invalid request method")
        return HttpResponseRedirect(reverse('main_app:checkout')) 


@login_required
def cancel(request, order_id):
    if request.method == 'POST':
        # Get the order object based on the order_id
        order = get_object_or_404(Order, pk=order_id)

        # Check if the status should be changed to Cancelled
        if order.status in ['pending', 'processing']:
            order.status = 'cancelled'
        else:
            order.status = 'returned'
            # Assuming you have additional logic for Return status, you can add it here

        order.save()  # Save the updated status

        # Redirect to the same page or any desired page after status change
        return redirect('main_app:orders')  # Assuming you have a URL named 'orders' defined in your urls.py file
    else:
        # Handle GET requests appropriately, if needed
        # For now, let's redirect to the 'orders' page
        return redirect('main_app:orders')
    
    

def base(request):
    return render(request,'main/base.html')

def temp(request):
    return render(request,'main/temparary.html')

