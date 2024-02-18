from django.shortcuts import render,redirect, get_object_or_404
from main_app.models import Main_Category, Product, ProductImage, ProductVariant, Brand, Banner
from gauth_app.models import Customer, Order, Coupon, Order_details
from django.contrib.auth import authenticate, login, logout 
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from django.views.decorators.cache import never_cache
from django.core.paginator import Paginator
from main_app.forms import BannerForm
from gauth_app.forms import CouponForm
from django.db.models import Sum, Count, F, DateField
from django.utils import timezone
import json
from datetime import date
from django.db.models.functions import TruncYear, TruncMonth
from django.http import JsonResponse
from django.http import HttpRequest
from django.http import HttpHeaders  # Add this import statement




     # ............. User Priventing Authentication...................
          
def superuser_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated or not request.user.is_superuser:
            return redirect('dashboard_app:dashboard_login') 
        return view_func(request, *args, **kwargs)
    return wrapper

#############################################################################################
                         # User management #
#############################################################################################


@superuser_required
def users(request):
    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        action = request.POST.get('action')

        user = Customer.objects.get(pk=user_id)
        if action == 'block':
            user.is_blocked = True
            messages.success(request, f"{user.email} is blocked.")
        elif action == 'unblock':
            user.is_blocked = False
            messages.success(request, f"{user.email} is unblocked.")

        user.save()

        return redirect('dashboard_app:users')

    # Order the records by email
    customers = Customer.objects.all().order_by('-id')
    return render(request, 'dashboard/users.html', {'customers': customers})


#############################################################################################
                            # Login and home #
#############################################################################################

   
# @superuser_required
# def dashboard(request):
#     orders = Order.objects.order_by("-id")
#     labels = []
#     data = []
#     for order in orders:
#         labels.append(str(order.id))
#         data.append(float(order.amount))  # Convert Decimal to float

#     total_customers = Customer.objects.count()

#     # Calculate the count of new users in the last one week
#     one_week_ago = timezone.now() - timezone.timedelta(weeks=1)
#     new_users_last_week = Customer.objects.filter(date_joined__gte=one_week_ago).count()

#     # Get the total number of orders
#     total_orders = Order.objects.count()

#     # Calculate the count of orders in the last one week
#     orders_last_week = Order.objects.filter(date__gte=one_week_ago).count()

#     # Calculate the total amount received
#     total_amount_received = Order.objects.aggregate(
#         total_amount_received=Cast(Sum(F('amount')), FloatField())
#     )['total_amount_received'] or 0

#     # Calculate the total amount received in the last week
#     total_amount_received_last_week = Order.objects.filter(date__gte=one_week_ago).aggregate(
#         total_amount_received=Cast(Sum(F('amount')), FloatField())
#     )['total_amount_received'] or 0
#     print(total_amount_received_last_week)


#     categories = Category.objects.annotate(num_products=Count('product'))
#     category_labels = [category.category_name for category in categories]
#     category_data = [category.num_products for category in categories]

#     total_products = Product.objects.count()

#     time_interval = request.GET.get('time_interval', 'all')  # Default to 'all' if not provided
#     if time_interval == 'yearly':
#         orders = Order.objects.annotate(date_truncated=TruncYear('date', output_field=DateField()))
#         orders = orders.values('date_truncated').annotate(total_amount=Sum('amount'))
#     elif time_interval == 'monthly':
#         orders = Order.objects.annotate(date_truncated=TruncMonth('date', output_field=DateField()))
#         orders = orders.values('date_truncated').annotate(total_amount=Sum('amount'))
#     else:
#         # Default to 'all' or handle other time intervals as needed
#         orders = Order.objects.annotate(date_truncated=F('date'))
#         orders = orders.values('date_truncated').annotate(total_amount=Sum('amount'))

#     # Calculate monthly sales
#     monthly_sales = Order.objects.annotate(
#         month=TruncMonth('date')
#     ).values('month').annotate(total_amount=Sum('amount')).order_by('month')

#     # Extract data for the monthly sales chart
#     monthly_labels = [entry['month'].strftime('%B %Y') for entry in monthly_sales]
#     monthly_data = [float(entry['total_amount']) for entry in monthly_sales]

#     # Add this block to handle AJAX request for filtered data
#     headers = HttpHeaders(request.headers)
#     is_ajax_request = headers.get('X-Requested-With') == 'XMLHttpRequest'

#     if is_ajax_request and request.method == 'GET':
#         time_interval = request.GET.get('time_interval', 'all')
#         filtered_labels = []
#         filtered_data = []

#         if time_interval == 'yearly':
#             filtered_orders = Order.objects.annotate(
#                 date_truncated=TruncYear('date', output_field=DateField())
#             )
#         elif time_interval == 'monthly':
#             filtered_orders = Order.objects.annotate(
#                 date_truncated=TruncMonth('date', output_field=DateField())
#             )
#         else:
#             # Default to 'all' or handle other time intervals as needed
#             filtered_orders = Order.objects.annotate(date_truncated=F('date'))

#         filtered_orders = filtered_orders.values('date_truncated').annotate(total_amount=Sum('amount')).order_by('date_truncated')

#         filtered_labels = [entry['date_truncated'].strftime('%B %Y') for entry in filtered_orders]
#         filtered_data = [float(entry['total_amount']) for entry in filtered_orders]

#         return JsonResponse({"labels": filtered_labels, "data": filtered_data})
#     context = {
#         "labels": json.dumps(labels),
#         "data": json.dumps(data),
#         "total_customers": total_customers,
#         "new_users_last_week": new_users_last_week,
#         "total_orders": total_orders,
#         "orders_last_week": orders_last_week,
#         "total_amount_received": total_amount_received,
#         "total_amount_received": total_amount_received_last_week,
#         "total_products": total_products,
#         "category_labels": json.dumps(category_labels),
#         "category_data": json.dumps(category_data),
#     }
#     context.update({
#         "monthly_labels": json.dumps(monthly_labels),
#         "monthly_data": json.dumps(monthly_data),
#     })

#     if "admin" in request.session:
#         return render(request, "dashboard/home.html", context)
#     else:
#         return redirect("admin")


@superuser_required
def dashboard_home(request):
    orders = Order_details.objects.order_by("-id")
    labels = []
    data = []
    for order in orders:
        labels.append(str(order.id))
        data.append(float(order.offer_price))
    total_customers = Customer.objects.count()

    one_week_ago = timezone.now() - timezone.timedelta(weeks=1)
    new_users_last_week = Customer.objects.filter(joined_date__gte=one_week_ago).count()

    total_orders = Order_details.objects.count()

    
    # Assuming you want to calculate the total offer_price for all Order_details instances
    total_offer_price_amount = Order_details.objects.aggregate(total_offer_price=Sum('offer_price'))

    # Extract the total offer_price from the result
    total_amount_received = total_offer_price_amount['total_offer_price'] or 0  # Handle None case


    # Filter Order_details objects for the last week
    order_details_last_week = Order_details.objects.filter(date__gte=one_week_ago)
    total_amount_received_last_week = order_details_last_week.aggregate(total_offer_price=Sum('offer_price'))
    # Extract the total offer price for last week from the result
    total_offer_price_last_week_value = total_amount_received_last_week['total_offer_price'] or 0  # Handle None case

    # Retrieve main categories and annotate them with the count of their related product variants
    main_categories = Main_Category.objects.annotate(num_product_variants=Count('product__productvariant'))
    # Extract main category labels and data
    category_labels = [category.name for category in main_categories]
    category_data = [category.num_product_variants for category in main_categories]

    total_products = ProductVariant.objects.count() 

    time_interval = request.GET.get('time_interval', 'all') # Default to "all" if we're not provided anything
    if time_interval == 'yearly':
        orders = Order_details.objects.annotate(date_truncated=TruncYear('date', output_field=DateField()))
        orders = orders.values('date_truncated').annotate(total_amount=Sum('offer_price')) 
    elif time_interval == 'monthly':
        orders = Order_details.objects.annotate(date_truncated=TruncMonth('date',output_field=DateField()))  
        orders = orders.values('date_truncated').annotate(total_amount=Sum('offer_price'))  


    monthly_sales = Order_details.objects.annotate(
        month=TruncMonth('date')
    ).values('month').annotate(total_amount=Sum('offer_price')).order_by('month')

    #Extract data for monthly sales chart
    monthly_labels = [entry['month'].strftime('%B %Y') for entry in monthly_sales]
    monthly_data = [float(entry['total_amount'])for entry in monthly_sales]
    monthly_data = [float(entry['total_amount']) for entry in monthly_sales]

    # Add this block to handle AJAX request for filtered data
    headers = HttpHeaders(request.headers)
    is_ajax_request = headers.get('X-Requested-With') == 'XMLHttpRequest'

    if is_ajax_request and request.method == 'GET':
        time_interval = request.GET.get('time_interval', 'all')
        filtered_labels = []
        filtered_data = []

        if time_interval == 'yearly':
            filtered_orders = Order.objects.annotate(
                date_truncated=TruncYear('date', output_field=DateField())
            )
        elif time_interval == 'monthly':
            filtered_orders = Order.objects.annotate(
                date_truncated=TruncMonth('date', output_field=DateField())
            )
        else:
            #Default to 'all' or handle other time intervals as needed
            filtered_orders = Order_details.annotate(date_truncated=F('date'))

        filtered_orders = filtered_orders.values('date_truncated').annotate(total_amount=Sum('offer_price')).order_by('date_truncated')
        filtered_labels = [entry['date_truncated'].strftime('%B %Y') for entry in filtered_orders]
        filtered_data = [float(entry['total_amount']) for entry in filtered_orders]

        return JsonResponse({"labels": filtered_labels, "data": filtered_data})

    context = {
        "labels": json.dumps(labels),
        "data": json.dumps(data),
        "total_customers": total_customers,
        "new_users_last_week": new_users_last_week,
        "total_orders": total_orders,
        "orders_last_week":  order_details_last_week,
        "total_amount_received": total_amount_received,
        "total_amount_received_last_week": total_amount_received_last_week,
        "total_products": total_products,
        "category_labels": json.dumps(category_labels),
        "category_data": json.dumps(category_data),
        "monthly_labels": json.dumps(monthly_labels),
        "monthly_data": json.dumps(monthly_data),
    }

    return render(request,'dashboard/home.html', context)


def dashboard_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        # Authenticate the user
        user = authenticate(request, username=username, password=password)

        if user is not None and user.is_superuser:
            # Log in the superuser
            login(request, user)
            return redirect("dashboard_app:dashboard_home")  # Redirect to your dashboard
        else:
            # Handle incorrect credentials
            messages.error(request, 'Invalid username or password. Please try again.')

    return render(request, 'dashboard/login.html')


def dashboard_logout(request):
    logout(request)
    return render(request,'dashboard/login.html')



#############################################################################################
            # Main Category Section, All product, Add, update and delete #
#############################################################################################


@superuser_required
def main_category(request):
    data = Main_Category.objects.all().order_by('id')
    return render(request,"dashboard/main_category.html",{"data": data})



@superuser_required
def add_main_category(request):
    if request.method == 'POST':
        main_category_name = request.POST['main_category_name']
        description = request.POST['description']
        image = request.FILES.get('image')
        delete = request.POST.get('delete', False) == 'True'
        
        # Check the category name is already there
        if Main_Category.objects.filter(name = main_category_name).exists():
            messages.error(request, "Category is already exists.")
            return render(request, 'dashboard/add_main_category.html')

        # Savin Data to the database
        query = Main_Category.objects.create(
            name=main_category_name,
            descriptions=description,
            img=image,
            deleted = delete
        )
        query.save()
        return redirect('dashboard_app:main_category')
    return render(request, 'dashboard/add_main_category.html')



@superuser_required
def update_main_category(request, id):
    data = Main_Category.objects.get(id=id)

    if request.method      == 'POST':
        main_category_name = request.POST['main_category_name']
        description        = request.POST['description']

        # Retrieve existing data
        edit = Main_Category.objects.get(id=id)

        # Update fields
        if Main_Category.objects.filter(name = main_category_name).exclude(id=id).exists():
            messages.error(request, "Category is already exists.")
            return render(request, 'dashboard/update_main_category.html', {"data": data})

            
        edit.name = main_category_name
        edit.descriptions = description 

        if 'image' in request.FILES:
            image = request.FILES['image']
            edit.img = image
        
        # Save updated data
        edit.save()

        return redirect('dashboard_app:main_category')

    return render(request, "dashboard/update_main_category.html", {"data": data})


@superuser_required
def soft_delete_category(request, id):
    data = Main_Category.objects.get(id=id)

    data.deleted = not data.deleted
    data.save()

    return redirect('dashboard_app:main_category')



def delete_main_category(request,id):
    data = Main_Category.objects.get(id=id) 
    data.delete()  
    return redirect('dashboard_app:main_category')



#############################################################################################
                             # Brand management #
#############################################################################################


@superuser_required
def brands(request):
    data = Brand.objects.all().order_by('id')
    return render(request, "dashboard/brands.html", {"data": data})


@superuser_required
def add_brand(request):
    if request.method == 'POST':
        name = request.POST['name']
        description = request.POST['description']
        image = request.FILES.get('image')
        delete = request.POST.get('delete', False) == 'True'
        
        # Check the category name is already there
        if Brand.objects.filter(name = name).exists():
            messages.error(request, "Category is already exists.")
            return render(request, 'dashboard/add_brand.html')

        # Savin Data to the database
        query = Brand.objects.create(
            name=name,
            description=description,
            image=image,
            deleted = delete
        )
        query.save()
        return redirect('dashboard_app:brands')
    return render(request, 'dashboard/add_brand.html')


@superuser_required
def update_brand(request, id):
    data = Brand.objects.get(id=id)

    if request.method      == 'POST':
        name               = request.POST['name']
        description        = request.POST['description']

        # Retrieve existing data
        edit = Brand.objects.get(id=id)

        # Update fields
        if Brand.objects.filter(name=name).exclude(id=id).exists():
            messages.error(request, "Another brand with this name already exists.")
            return render(request, 'dashboard/update_brand.html', {"data": data})
            
        edit.name = name
        edit.description = description 


        if 'image' in request.FILES:
            image = request.FILES['image']
            edit.image = image
        
        # Save updated data
        edit.save()

        return redirect('dashboard_app:brands')

    return render(request, "dashboard/update_brand.html", {"data": data})




@superuser_required
def delete_brand(request, id):
    data = Brand.objects.get(id=id)

    data.deleted = not data.deleted
    data.save()

    return redirect('dashboard_app:brands')



#############################################################################################
       # Product Section, contains "all_products, add, update and delete product" #
#############################################################################################


@superuser_required
def products(request):
    items = Product.objects.all().order_by('-id')
    p = Paginator(items, 6)
    page = request.GET.get('page')
    data = p.get_page(page)
    return render(request, "dashboard/products.html", {"data": data})


def add_product(request):
    data = Main_Category.objects.all()
    brand = Brand.objects.all() 

    if request.method == 'POST':
        # Extracting data from the POST request
        model = request.POST['model']
        description = request.POST['description']
        color = request.POST['color']
        display_size = request.POST['display_size']
        camera = request.POST.get('camera', '')  # Get camera data or empty string if not provided
        battery = request.POST.get('battery', '')  # Get battery data or empty string if not provided
        network = request.POST.get('network', False) == 'true'
        smart = request.POST.get('smart', False) == 'true'
        image = request.FILES.get('image')
        main_category_id = request.POST.get('main_category_id')  
        brand_id = request.POST.get('brand')

        # Getting brand and main category objects
        brand = Brand.objects.get(id=brand_id)
        main_cat = Main_Category.objects.get(id=main_category_id)

        # Create the Product instance with the calculated offer price
        query = Product.objects.create(
            brand=brand,
            model=model,
            description=description,
            color=color,
            display_size=display_size,
            camera=camera if camera else None,  # Save camera if provided, else save None
            network=network,
            smart=smart,
            battery=battery if battery else None,  # Save battery if provided, else save None
            image=image,
            main_category=main_cat,
        )

        # Save multiple images associated with the product
        images = request.FILES.getlist('images')
        for img in images:
            ProductImage.objects.create(product=query, image=img)
            
        return redirect('dashboard_app:products')

    context = {
        "data" : data,
        "brand" : brand
    }

    # Render the form if it's not a POST request
    return render(request, 'dashboard/add_product.html', context)


@superuser_required
def update_product(request, id):
    data = Main_Category.objects.all()
    brands = Brand.objects.all()
    product = Product.objects.get(id=id)

    if request.method == 'POST':
        model = request.POST['model']
        description = request.POST['description']
        color = request.POST['color']
        display_size = request.POST['display_size']
        camera = request.POST.get('camera', '')  # Get camera with default empty string
        network = request.POST.get('network', False)
        smart = request.POST.get('smart', False)
        battery = request.POST.get('battery', '')  # Get battery with default empty string
        images = request.FILES.getlist('images')
        brand_id = request.POST.get('brand')
        main_cat_id = request.POST.get('phone_category')
        brand = Brand.objects.get(id=brand_id)
        main_cat = Main_Category.objects.get(id=main_cat_id)

        # Retrieve existing data
        edit = Product.objects.get(id=id)

        # Update data in the table
        edit.brand = brand
        edit.main_category = main_cat  
        edit.model = model
        edit.description = description
        edit.color = color
        edit.display_size = display_size
        edit.camera = camera if camera else None  # Set to None if camera is empty
        edit.network = network
        edit.smart = smart
        edit.battery = battery if battery else None  # Set to None if battery is empty

        # Update main image only if the user provided
        if 'image' in request.FILES:
            image = request.FILES['image']
            edit.image = image

        edit.save()

        # Remove existing images associated with the product
        existing_images = ProductImage.objects.filter(product=edit)
        for existing_image in existing_images:
            existing_image.delete()

        # Save multiple new images associated with the product
        for img in images:
            ProductImage.objects.create(product=edit, image=img)

        return redirect('dashboard_app:products')

    context = {
        'product': product,
        'data': data,
        'brands': brands,
    }

    return render(request, "dashboard/update_product.html", context)



@superuser_required
def soft_delete_product(request, id):
    product = ProductVariant.objects.get(id=id)

    product.deleted = not product.deleted
    product.save()

    return redirect('dashboard_app:all_products')



@superuser_required
def delete_product(request,id):
    data = Product.objects.get(id=id) 
    data.delete()  
    return redirect('dashboard_app:all_products')



#############################################################################################
                        # Product Varinats management #
#############################################################################################




@superuser_required
def all_products(request):
    product_variants = ProductVariant.objects.all().order_by('-id')
    paginator = Paginator(product_variants, 6)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'dashboard/all_products.html', {'products': page_obj})


@superuser_required
def add_variant(request, id):
    product = Product.objects.get(id=id)
    if request.method == 'POST':
        # Extracting data from the POST request
        price = request.POST['price']
        ram = request.POST['ram']
        storage = request.POST['storage']
        stock = request.POST['stock']
        offer = request.POST['offer'] 
        product_id = request.POST.get('product_id')
        delete = request.POST.get('delete', False) == 'True'


        # Calculate offer price
        offer_price = int(price) - (int(price) * int(offer) / 100)

        # Create the Product instance with the calculated offer price
        query = ProductVariant.objects.create(
            price=price,
            ram=ram,
            storage=storage,
            stock=stock,
            offer=offer,
            offer_price=offer_price,
            product = product,
            deleted=delete,

        )
  
        return redirect('dashboard_app:products')

    # Render the form if it's not a POST request
    return render(request, 'dashboard/add_variant.html', {'product':product})


@superuser_required
def update_variant(request, id):
    variant = ProductVariant.objects.get(id=id)

    if request.method == 'POST':
        price = request.POST['price']
        ram = request.POST['ram']
        storage = request.POST['storage']
        stock = request.POST['stock']
        offer = request.POST['offer']
        delete = request.POST.get('delete', False)

        # Convert offer to an integer
        offer = int(offer)

        # Calculate offer price
        offer_price = int(price) - (int(price) * offer / 100)

        # Update data in the table
        variant.price = price
        variant.ram = ram
        variant.storage = storage
        variant.stock = stock
        variant.offer = offer
        variant.offer_price = offer_price
        variant.deleted = delete
        variant.save()
        
        return redirect('dashboard_app:all_products')

    context = {'variant':variant}
    return render(request, "dashboard/update_variant.html", context)



#############################################################################################
                                  # Orders #
#############################################################################################


@superuser_required
def orders(request):
    # Filter orders by the current user
    user_orders = Order.objects.all().order_by('-id')

    # Render the orders template with user's orders data
    return render(request, 'dashboard/orders.html', {'orders': user_orders})


@superuser_required
def update_order_status(request, order_id):
    if request.method == 'POST':
        new_status = request.POST.get('new_status')
        order = Order.objects.get(pk=order_id)
        order.status = new_status
        order.save()
    return redirect('dashboard_app:orders')



#############################################################################################
                             # Banner Management #
#############################################################################################


@superuser_required
def banners(request):
    banners = Banner.objects.all().order_by('-id')
    
    return render(request, 'dashboard/banners.html', {'banners': banners})

@superuser_required
def add_banners(request):
    if request.method == "POST":
        form = BannerForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('dashboard_app:banners')
    else:
        form = BannerForm()
    return render(request, 'dashboard/add_banners.html', {'form':form})


def update_banners(request, id):
    # Fetch the existing banner object from the database
    banner = get_object_or_404(Banner, pk=id)
 
    if request.method == 'POST':
        # If the form is submitted with data, process the form
        form = BannerForm(request.POST, request.FILES, instance=banner)
        if form.is_valid():
            form.save()
            # Redirect to the updated banner detail page
            return redirect('dashboard_app:banners')  # Assuming you have a 'banners' URL defined
        else:
            # If form validation fails, render the form again with validation errors
            return render(request, 'dashboard/update_banner.html', {'form': form, 'banner': banner})
    else:
        # If the request is a GET request, pre-fill the form with the existing banner details
        form = BannerForm(instance=banner)
    
    # Render the template with the form and the existing banner object
    return render(request, 'dashboard/update_banner.html', {'form': form, 'banner': banner})


@superuser_required
def delete_banner(request, id):
    data = Banner.objects.get(id=id)

    data.deleted = not data.deleted
    data.save()

    return redirect('dashboard_app:banners')


#############################################################################################
                             # COUPON MANAGEMENT #
#############################################################################################


def coupons(request):
    coupons = Coupon.objects.all().order_by('-id')
    context = {
        'coupons':coupons,

    }   
    return render(request, 'dashboard/coupons.html', context)


def add_coupon(request):
    if request.method == 'POST':
        form = CouponForm(request.POST)
        if form.is_valid():
            form.save()
            # Optionally, you can add a success message here
            return redirect('dashboard_app:coupons') 
    else:
        form = CouponForm()
    return render(request, 'dashboard/add_coupon.html', {'form': form})


@superuser_required
def delete_coupon(request, id):
    data = Coupon.objects.get(id=id)
    data.valid = not data.valid
    data.save()
    
    return redirect('dashboard_app:coupons')


def update_coupon(request, id):
    # Fetch the existing banner object from the database
    coupon = get_object_or_404(Coupon, pk=id)
 
    if request.method == 'POST':
        form = CouponForm(request.POST, request.FILES, instance=coupon)
        if form.is_valid():
            form.save()
            return redirect('dashboard_app:coupons') 
        else:
            # If form validation fails, render the form again with validation errors
            return render(request, 'dashboard/update_banner.html', {'form': form, 'coupon': coupon})
    else:
        # If the request is a GET request, pre-fill the form with the existing banner details
        form = form = CouponForm(instance=coupon)
    
    # Render the template with the form and the existing banner object
    return render(request, 'dashboard/update_coupon.html', {'form': form, 'coupon': coupon})



#############################################################################################
                             # COUPON MANAGEMENT #
#############################################################################################


 