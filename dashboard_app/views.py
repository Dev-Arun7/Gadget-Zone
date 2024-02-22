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
from datetime import datetime
import json
from datetime import date
from django.db.models.functions import TruncYear, TruncMonth
from django.http import JsonResponse, HttpRequest, HttpHeaders, HttpResponse, FileResponse
from django.db.models import Q
import io
from reportlab.platypus import SimpleDocTemplate
from reportlab.lib.pagesizes import A4, inch
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from django.views.decorators.http import require_http_methods




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

  

@require_http_methods(["GET"])
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
    total_amount_received //= 1000

    # Filter Order_details objects for the last week
    order_details_last_week = Order_details.objects.filter(date__gte=one_week_ago)

    # Count the number of orders from last week
    total_orders_last_week = order_details_last_week.count()

    # Calculate the total offer price for order details from last week
    total_amount_received_last_week_details = order_details_last_week.aggregate(total_offer_price=Sum('offer_price'))

    # Extract the total offer price for last week from the result
    total_amount_received_last_week = total_amount_received_last_week_details['total_offer_price'] or 0  # Handle None case
    total_amount_received_last_week //= 1000

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
        "total_orders_last_week": total_orders_last_week,
        "total_amount_received": total_amount_received,
        "total_amount_received_last_week": total_amount_received_last_week,
        "total_products": total_products,
        "category_labels": json.dumps(category_labels),
        "category_data": json.dumps(category_data),
        "monthly_labels": json.dumps(monthly_labels),
        "monthly_data": json.dumps(monthly_data),
    }


    if request.method == 'GET':
        # Get the start and end dates from the request GET parameters
        from_date_str = request.GET.get('from_date')
        to_date_str = request.GET.get('to_date')

        # Convert string dates to datetime objects
        if from_date_str and to_date_str:
            from_date = datetime.strptime(from_date_str, '%Y-%m-%d')
            to_date = datetime.strptime(to_date_str, '%Y-%m-%d')

            # Filter Order_details objects based on the provided dates
            filtered_orders = Order_details.objects.filter(date__range=[from_date, to_date])
            order_count = filtered_orders.count()

            filtered_customers_details = Customer.objects.filter(joined_date__range=[from_date, to_date])
            filtered_customers = filtered_customers_details.count()

            # Aggregate the total offer price for the filtered orders
            total_amount_received = filtered_orders.aggregate(total_offer_price=Sum('offer_price'))

            # Extract the total offer price from the result
            total_amount = total_amount_received['total_offer_price'] or 0
            total_amount //= 1000

            # Prepare the filtered data for rendering in the HTML template
            data = []
            labels = []
            for order in filtered_orders:
                data.append(float(order.offer_price))
                labels.append(str(order.id))


            # Update the context with filtered data
            context.update({
                'total_orders': order_count,
                'total_amount_received': total_amount,
                'total_customers' : filtered_customers,
                "labels": json.dumps(labels),
                'data': json.dumps(data),
            })
    
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
        offer = request.POST['offer']
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
            offer = offer,
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
        offer              = request.POST['offer']

        # Retrieve existing data
        edit = Main_Category.objects.get(id=id)

        # Update fields
        if Main_Category.objects.filter(name = main_category_name).exclude(id=id).exists():
            messages.error(request, "Category is already exists.")
            return render(request, 'dashboard/update_main_category.html', {"data": data})

            
        edit.name = main_category_name
        edit.descriptions = description 
        edit.offer = offer

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

    print("xxxxxxxx", items)
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



def product_search(request):
    if request.method == "POST":
        searched = request.POST.get('searched')

        # Query products by model or brand name
        products_by_model = Product.objects.filter(model__icontains=searched)
        products_by_brand = Product.objects.filter(brand__name__icontains=searched)

        # Combine the querysets to get unique products
        products = (products_by_model | products_by_brand).distinct()

        context = {
            'data': products,
        }
        print(context)
        return render(request, 'dashboard/products.html', context)

    return redirect('dashboard_app:home')


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


def variant_search(request):
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
        return render(request, 'dashboard/all_products.html', context)

    return redirect('dashboard_app:home')


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


@superuser_required
def coupons(request):
    coupons = Coupon.objects.all().order_by('-id')
    context = {
        'coupons':coupons,

    }   
    return render(request, 'dashboard/coupons.html', context)


@superuser_required
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
@superuser_required
def delete_coupon(request, id):
    data = Coupon.objects.get(id=id)
    data.valid = not data.valid
    data.save()
    
    return redirect('dashboard_app:coupons')


@superuser_required
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


 
@superuser_required
def filter_sales(request):
    time_interval = request.GET.get('time_interval', 'all')

    if time_interval == 'yearly':
        # Filter data for yearly sales
        filtered_data = Order_details.objects.annotate(
            date_truncated=TruncYear('date')
        ).values('date_truncated').annotate(total_amount=Sum('amount')).order_by('date_truncated')

    elif time_interval == 'monthly':
        # Filter data for monthly sales
        filtered_data = Order_details.objects.annotate(
            date_truncated=TruncMonth('date')
        ).values('date_truncated').annotate(total_amount=Sum('amount')).order_by('date_truncated')

    else:
        # Default to 'all' or handle other time intervals as needed
        # Here, we are using DateTrunc to truncate the date to a day
        filtered_data = Order_details.objects.annotate(
            date_truncated=TruncDate('day', 'date')
        ).values('date_truncated').annotate(total_amount=Sum('amount')).order_by('date_truncated')

    # Extract data for the filtered chart
    filtered_labels = [entry['date_truncated'].strftime('%B %Y') for entry in filtered_data]
    filtered_data = [float(entry['total_amount']) for entry in filtered_data]

    return JsonResponse({"labels": filtered_labels, "data": filtered_data})





def report_generator(request, orders):
    from_date_str = request.POST.get('from_date')
    to_date_str = request.POST.get('to_date')

    from_date = datetime.strptime(from_date_str, '%Y-%m-%d').date()
    to_date = datetime.strptime(to_date_str, '%Y-%m-%d').date()

    if from_date > date.today() or to_date > date.today():
        # Return an error response or show a message
        return HttpResponse('Please enter a valid date.')

    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=18)
    story = []

    data = [["Order ID", "Total Quantity", "Product IDs", "Product Names", "Amount"]]

    total_sales_amount = 0  # Initialize total sales amount sum

    print("xxxxxxxxxxx",orders)

    for order in orders:
        # Retrieve order items associated with the current order
        order_items = Order_details.objects.filter(order_id=order.pk)
        total_quantity = 0
        product_ids = ""
        product_names = ""

        # for item in order_items:
        #     total_quantity += item.quantity
        #     product_ids += str(item.order.variant.id) + ", "
        #     product_names += str(item.order.product.model) + ", "

        # # Remove the trailing comma and space from the product IDs and names
        # product_ids = product_ids.rstrip(", ")
        # product_names = product_names.rstrip(", ")

        total_quantity =order.quantity
        product_ids = order.order.product.id
        product_names = order.order.product.brand.name
        product_names += " " + order.order.product.model
        

        order_amount = order.offer_price
        total_sales_amount += order_amount  # Accumulate total sales amount

        data.append([order.id, total_quantity, product_ids, product_names, order_amount])

    # Add a row for the total sales amount at the end of the table
    data.append(["Total Sales", "", "", "", total_sales_amount])

    # Create a table with the data
    table = Table(data, colWidths=[1 * inch, 1.5 * inch, 2 * inch, 3 * inch, 1 * inch])

    # Style the table
    table_style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.gray),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 14),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -2), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 2),
        ('BOTTOMPADDING', (0, -1), (-1, -1), 6),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
    ])
    table.setStyle(table_style)

    # Add the table to the story and build the document
    story.append(table)
    doc.build(story)

    buf.seek(0)
    return FileResponse(buf, as_attachment=True, filename='orders_report.pdf')








def report_pdf_order(request):
    if request.method == 'POST':
        from_date = request.POST.get('from_date')
        to_date = request.POST.get('to_date')
        try:
            from_date = datetime.strptime(from_date, '%Y-%m-%d').date()
            to_date = datetime.strptime(to_date, '%Y-%m-%d').date()
        except ValueError:
            return HttpResponse('Invalid date format.')
        orders = Order_details.objects.filter(date__range=[from_date, to_date]).order_by('-id')
        print("yyyyyyyyy",orders)
        return report_generator(request, orders)
    
    