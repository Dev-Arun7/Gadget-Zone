from django.shortcuts import render, redirect
from main_app.models import Main_Category, Product, ProductVariant, Brand
from gauth_app.models import Cart, Wishlist, Address, Order, Order_details, Wishlist, Wallet, Coupon
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.db.models import Q
from django.contrib import messages
from django.db.models import Sum
from django.urls import reverse
import json
import random
from django.core.paginator import Paginator
from decimal import Decimal
from random import shuffle
from datetime import date

#Razorpay
from django.conf import settings
import razorpay
import json
from django.views.decorators.csrf import csrf_exempt



def home(request):
    # Retrieve first 10 products ordered by ID
    products = list(ProductVariant.objects.filter(deleted=False).order_by('-id')[:10])

    # Retrieve first 10 deals ordered by offer
    deals = list(ProductVariant.objects.filter(deleted=False).order_by('-offer')[:12])

    # Retrieve all brands in random order
    brands = list(Brand.objects.all().order_by('?'))

    # Shuffle the first 10 deals and products separately
    shuffle(products)
    shuffle(deals)

    context = {
        'products': products, 
        'brands': brands,
        'deals': deals,
    }  
    return render(request, "main/home.html", context)


def product_list(request):
    # Retrieve all products
    products = ProductVariant.objects.filter(deleted=False).order_by('-id')
    brands = Brand.objects.all()

    # Filter products based on user input
    if request.GET:
        category_ids = request.GET.getlist('category')
        brand_ids = request.GET.getlist('brand')
        price_ranges = request.GET.getlist('price_range')  
        ram_values = request.GET.getlist('ram') 
        color_values = request.GET.getlist('color_range')

        # Filter by category
        if category_ids:
            products = products.filter(product__main_category__id__in=category_ids)

        # Filter by brand
        if brand_ids:
            products = products.filter(product__brand__id__in=brand_ids)

        # Filter by price range
        for price_range in price_ranges:
            min_price, max_price = map(int, price_range.split('-'))
            products = products.filter(price__range=(min_price, max_price))

        # Filter by color
        if color_values:
            # Assuming color is a field in ProductVariant model
            products = products.filter(product__color__in=color_values)


    # Paginator
    items_per_page = 9
    paginator = Paginator(products, items_per_page)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'products': page_obj,
        'brands': brands,
    }
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


def brand_products(request, id):
    product_variants = ProductVariant.objects.filter(product__brand_id=id, deleted=False)
    return render(request, "main/product_list.html", {'products': product_variants})


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



def sort(request):
    products = ProductVariant.objects.filter(deleted=False).order_by('-id')  # Retrieve all products initially

    # Sorting logic
    sort_by = request.GET.get('sort_by')
    if sort_by:
        if sort_by == 'price+':
            products = products.order_by('offer_price')
        elif sort_by == 'price-':
            products = products.order_by('-offer_price')
        elif sort_by == 'name+':
            products = products.order_by('product__model')
        elif sort_by == 'release_date-':
            products = products.order_by('-product__id')

    return render(request, 'main/product_list.html', {'products': products})


###############################################################################################################
                                # Cart and Wishlist #
###############################################################################################################


@login_required
def cart(request):
    # Retrieve all cart items along with related product and product variant details
    cart_items = Cart.objects.select_related('product', 'product_variant').filter(user=request.user).order_by('-id')
    
    # setting coupon as non initially
    request.session['coupon'] = None

    # Calculate subtotal for each item and total price for all items in the cart
    total_price = 0
        # Initialize coupon_code
    coupon_code = None
    coupon_amount = 0

    for item in cart_items:
        # Check if there is sufficient stock for the product variant
        if item.quantity <= item.product_variant.stock:
            # Calculate subtotal for the item
            item.subtotal = item.quantity * item.product_variant.offer_price
            # Add subtotal to the total price
            total_price += item.subtotal

    # Handle coupon application
    if request.method == 'POST':
        coupon_code = request.POST.get('coupon_code')
        try:
            coupon = Coupon.objects.get(coupon=coupon_code, valid=True, date__gte=date.today())
            if coupon.min_amount is not None and total_price < coupon.min_amount:
                messages.error(request, f"Minimum purchase amount for '{coupon_code}' is {coupon.min_amount}")
            else:
                # Apply coupon logic here
                # For example, calculate the new total price after applying the coupon
                total_price -= coupon.amount
                request.session['coupon'] = coupon_code

                # Assign coupon amount to show on the page
                coupon_amount = coupon.amount

                # Show success message after applying the coupon
                messages.success(request, 'Coupon applied successfully!')

        except Coupon.DoesNotExist:
            messages.error(request, f"Invalid or expired coupon code: {coupon_code}")

            # Redirect back to the cart page to reflect the changes
            return redirect('main_app:cart')

    context = {'cart': cart_items,
    'coupon_code': coupon_code,
     'subtotal': total_price,
     'coupon_amount': coupon_amount
     }
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
                    # Check if the product is in the user's wishlist and remove it if found.
                    if Wishlist.objects.filter(user=request.user, product=product, product_variant=variant).exists():
                        wishlist_item = Wishlist.objects.get(user=request.user, product=product, product_variant=variant)
                        wishlist_item.delete()

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
                                 # WISH LIST #
###############################################################################################################

def wishlist(request):
    products = Wishlist.objects.select_related('product', 'product_variant').filter(user=request.user).order_by('-id')
    return render(request, 'main/wishlist.html', {'products':products})


def add_to_wish(request, product_id, variant_id):
    if request.method == 'POST':
        if request.user.is_authenticated:
            product = get_object_or_404(Product, id=product_id)
            variant = get_object_or_404(ProductVariant, id=variant_id)

            # Check if the product exists.
            if product:
                # Check if the product is already in the user's cart.
                if Wishlist.objects.filter(user=request.user, product=product, product_variant=variant).exists():
                    return JsonResponse({'status': "Product Already in wishlist..!", 'added': False})
                else: 
                    # Create a new Cart object for the user and add the product.
                    Wishlist.objects.create(user=request.user,
                                        product=product,
                                        product_variant=variant,
                                        )
                    # Return success message
                    return JsonResponse({'status': "Product added successfully", 'added': True})
        else:
            return JsonResponse({'status': "Login to continue"})

    # If the request method is not POST, redirect to the home page.
    return redirect('main_app:home')



@login_required
def delete_wish(request, product_id):
    try:
        cart_item = Wishlist.objects.get(id=product_id)
    except Wishlist.DoesNotExist:
        return redirect('main_app:wishlist')
    
    cart_item.delete()
    return redirect('main_app:wishlist')


###############################################################################################################
                                # Checkout and Order #
###############################################################################################################


@login_required
def orders(request):
    # Filter orders by the current user
    user_orders = Order.objects.filter(user=request.user).order_by('-id')

    # Render the orders template with user's orders data
    return render(request, 'main/orders.html', {'orders': user_orders})



@login_required
def checkout(request):
    cart_items = Cart.objects.filter(quantity__gt=0)
    
    # Check if all products in the cart are in stock
    for item in cart_items:
        if item.product_variant.stock < item.quantity:
           messages.warning(request, "Some items are out of stock.")
           return redirect('main_app:cart')

    # Retrieve the coupon code from the session
    coupon_code = request.session.get('coupon', None)
    
    # If all products are in stock, proceed with the checkout process
    addresses = Address.objects.filter(user=request.user)
    total_price = cart_items.aggregate(total_price=Sum('total'))['total_price'] or 0

    # Apply coupon discount if it exists
    if coupon_code:
        try:
            coupon = Coupon.objects.get(coupon=coupon_code, valid=True, date__gte=date.today())
            total_price -= coupon.amount
        except Coupon.DoesNotExist:
            # Handle the case if the coupon does not exist
            messages.error(request, f"Invalid or expired coupon code: {coupon_code}")

    context = {
        'subtotal': total_price,
        'addresses': addresses,
    }
    return render(request, "main/checkout.html", context)




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

        # If any item is out of stock, return to checkout page
        if out_of_stock_items:
            messages.warning(request, "Some items are out of stock. Please remove them from your cart.")
            return HttpResponseRedirect(reverse('main_app:cart'))
            
        # Proceed with order placement for in-stock items
        total_offer_price = 0
        total_price = 0
        total_quantity = 0
        for cart_item in in_stock_items:
            order = Order.objects.create(
                user=user,
                address_id=address_id,
                product=cart_item.product,
                amount=cart_item.total,
                payment_type=payment_type, 
                status='pending',
                quantity=cart_item.quantity,
                variant=cart_item.product_variant
            )
            
            total_offer_price += cart_item.total
            total_price += cart_item.product_variant.price * cart_item.quantity
            total_quantity += cart_item.quantity

            cart_item.product_variant.stock -= cart_item.quantity
            cart_item.product_variant.save()
            cart_item.delete()
        # Update Order_details model
        Order_details.objects.create(
            order = order,
            user = user,
            quantity = total_quantity,
            offer_price = total_offer_price,
            price_total = total_price
        )

        # After placing the order, make the applied coupon invalid
        applied_coupon = request.session.get('coupon')
        if applied_coupon:
            try:
                coupon = Coupon.objects.get(coupon=applied_coupon, valid=True)
                coupon.valid = False
                coupon.save()
                del request.session['coupon'] # Removing the applied coupon from the session
            except Coupon.DoesNotExist:
                pass # no need to do if the coupon is alredy invalid 

        return HttpResponseRedirect(reverse('main_app:home') + '?success=true')
        payMode = request.POST.get('payment_type')
        if (payMode == 'razorpay'):
            return JasonResponse({'status': "Razorpay is done"})
         
    else:
        messages.error(request, "Invalid request method")
        return HttpResponseRedirect(reverse('main_app:checkout'))


@login_required
def razorpay(request):
    user = request.user
    cart_items = Cart.objects.filter(user=user, quantity__gt=0)
    in_stock_items = []
    out_of_stock_items = []

    for cart_item in cart_items:
        if cart_item.quantity <= cart_item.product_variant.stock:
            in_stock_items.append(cart_item)
        else:
            out_of_stock_items.append(cart_item)

    # If any item is out of stock, return to checkout page
    if out_of_stock_items:
        messages.warning(request, "Some items are out of stock. Please remove them from your cart.")
        return HttpResponseRedirect(reverse('main_app:cart'))

    total_offer_price = 0
    for item in in_stock_items:
        total_offer_price += item.product_variant.offer_price * item.quantity

    total_offer_price += 50 # Adding shipping charge

    return JsonResponse({
        'total_offer_price': total_offer_price
    })




@login_required
def cancel(request, order_id):
    if request.method == 'POST':
        # Get the order object based on the order_id
        order = get_object_or_404(Order, pk=order_id)

        # Check if the status should be changed to Cancelled
        if order.status in ['pending', 'processing', 'shipped']:
            order.status = 'cancelled'
        else:
            order.status = 'returned'

        variant = order.variant
        variant.stock += order.quantity
        variant.save()
        # Return amount to user's wallet
        user = request.user
        try:
            # Retrieve user's wallet
            wallet = Wallet.objects.get(user=user)
        except Wallet.DoesNotExist:
            # If wallet doesn't exist, create one for the user
            wallet = Wallet.objects.create(user=user)

        # Add the amount of cancelled order to the wallet balance
        wallet.balance += Decimal(order.amount)
        wallet.save()

        order.save()  # Save the updated status

        # Redirect to the same page or any desired page after status change
        return redirect('main_app:orders')  # Assuming you have a URL named 'orders' defined in your urls.py file
    else:
        # Handle GET requests appropriately, if needed
        # For now, let's redirect to the 'orders' page
        return redirect('main_app:orders')



def order_detail(request, id):
    product = get_object_or_404(Order, id=id)
    context = {
        'product' : product
    }
    
    return render(request, "main/order_detail.html", context)
    
    

def base(request):
    return render(request,'main/base.html')

def temp(request):
    return render(request,'main/temparary.html')

