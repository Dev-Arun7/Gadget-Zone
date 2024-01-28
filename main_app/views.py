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


def home(request):
    products = Product.objects.prefetch_related('productvariant_set').filter(deleted=False).order_by('id').reverse()
    context = {'products': products}    
    return render(request, "main/home.html", context)


def product_list(request):
    products = Product.objects.prefetch_related('productvariant_set').all().order_by('id')
    context = {'products': products}
    return render(request, "main/product_list.html", context)



def category_products(request,id):
    main_category = Main_Category.objects.get(pk=id)
    products = Product.objects.filter(main_category=main_category, deleted=False)
    for product in products:
        product.offer_price = int(product.price * (1 - product.offer / 100))
    return render(request, "main/product_list.html", {'data': products})


def single_product(request, id, variant_id):
    # Get the product and its variants
    product = get_object_or_404(Product, id=id)

    # Fetch the specific variant using the provided variant_id
    variant = get_object_or_404(ProductVariant, id=variant_id, product=product)

    variants = product.productvariant_set.all()  # Use the related name 'productvariant_set' to access variants

    # Fetch additional images from the related ProductImage model
    additional_images = product.additional_images.all()

    # Similar Products
    similar_products = Product.objects.filter(main_category_id=product.main_category_id, deleted=False).prefetch_related('productvariant_set').exclude(id=id)

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
    # Retrieve all cart items along with related product and product variant details
    cart_items = Cart.objects.select_related('product', 'product_variant').filter(user=request.user)

    # Calculate subtotal for each item and total price for all items in the cart
    total_price = 0
    valid_cart_items = []  # List to store cart items with valid stock

    for item in cart_items:
        # Check if there is sufficient stock for the product variant
        if item.quantity <= item.product_variant.stock:
            # Calculate subtotal for the item
            item.subtotal = item.quantity * item.product_variant.offer_price
            # Add subtotal to the total price
            total_price += item.subtotal
            # Append the item to the list of valid cart items
            valid_cart_items.append(item)

    context = { 'cart': valid_cart_items, 'subtotal': total_price }
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
                    return JsonResponse({'status': "Product Already in cart..!"})
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
        prod_id = int(request.POST.get('product_id'))
        var_id = int(request.POST.get('variant_id'))
        
        if Cart.objects.filter(user=request.user, product_id=prod_id, product_variant_id=var_id).exists():
            prod_qty = int(request.POST.get('product_qty'))
            cart_data = Cart.objects.get(product_id=prod_id, product_variant_id=var_id, user=request.user)
            
            # Check if requested quantity exceeds available stock
            available_stock = cart_data.product_variant.stock
            if prod_qty > available_stock:
                # Update cart with maximum available stock
                cart_data.quantity = available_stock
                cart_data.total = available_stock * cart_data.product_variant.offer_price
                cart_data.save()
                return JsonResponse({'status': f"Quantity updated to maximum available stock: {available_stock}", 'redirect_url': '/home/'})
            
            # If requested quantity is within available stock, update cart normally
            cart_data.quantity = prod_qty
            cart_data.total = prod_qty * cart_data.product_variant.offer_price
            cart_data.save()
            print(cart_data)
            return JsonResponse({'status': "Updated Successfully", 'redirect_url': '/home/'})
        
        else:
            return JsonResponse({'status': "Product not found in cart", 'redirect_url': '/home/'})
    
    return JsonResponse({'status': "Invalid Request", 'redirect_url': '/cart/'})





def delete_cart(request, product_id):
    # Retrieve the cart item to delete
    cart_item = get_object_or_404(Cart, id=product_id)
    cart_item.delete()
    return redirect('main_app:cart') 


###############################################################################################################
                                # Checkout and Order #
###############################################################################################################



def checkout(request):

    cart_items = Cart.objects.filter(quantity__gt=0, product_variant__stock__gt=0)
    addresses = Address.objects.filter(user=request.user)
    total_price = cart_items.aggregate(total_price=Sum('total'))['total_price'] or 0

    context = { 'subtotal': total_price,
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


def place_order(request):
    if request.method == 'POST':
        user = request.user
        address_id = request.POST.get('addressId')
        payment_type = request.POST.get('payment')  

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
                image=cart_item.image
            )
            cart_item.product_variant.stock -= cart_item.quantity
            cart_item.product_variant.save()
            cart_item.delete()

        if out_of_stock_items:
            messages.warning(request, "Some items are out of stock and were not included in the order.")

        return HttpResponseRedirect(reverse('main_app:home') + '?success=true')
    else:
        messages.error(request, "Invalid request method")
        return redirect('checkout')
  


def base(request):
    return render(request,'main/base.html')

def temp(request):
    return render(request,'main/temparary.html')

