from django.shortcuts import render,redirect
from main_app.models import Main_Category, Product
from gauth_app.models import Customer
from django.contrib.auth import authenticate, login, logout 
from django.contrib.auth.decorators import login_required
from django.contrib import messages


#############################################################################################
                         # User management #
#############################################################################################


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
    customers = Customer.objects.all().order_by('email')
    return render(request, 'dashboard/users.html', {'customers': customers})

#############################################################################################
                            # Login and home #
#############################################################################################

from django.contrib import messages  # Import the messages module

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


@login_required(login_url='dashboard_app:dashboard_login')
def dashboard_home(request):
    return render(request,'dashboard/home.html')

#############################################################################################
            # Main Category Section, All product, Add, update and delete #
#############################################################################################

@login_required(login_url='dashboard_app:dashboard_login')
def main_category(request):
    data = Main_Category.objects.all()
    return render(request,"dashboard/main_category.html",{"data": data})


@login_required(login_url='dashboard_app:dashboard_login')
def add_main_category(request):
    if request.method == 'POST':
        main_category_name = request.POST['main_category_name']
        description = request.POST['description']
        image = request.FILES.get('image')

        # Savin Data to the database
        query = Main_Category.objects.create(
            name=main_category_name,
            descriptions=description,
            img=image,
        )
        query.save()
        return redirect('main_category')
    return render(request, 'dashboard/add_main_category.html')


@login_required(login_url='dashboard_app:dashboard_login')
def update_main_category(request, id):
    data = Main_Category.objects.get(id=id)

    if request.method == 'POST':
        main_category_name = request.POST['main_category_name']
        description        = request.POST['description']
        image              = request.FILES.get('image')

        # Retrieve existing data
        edit = Main_Category.objects.get(id=id)

        # Update fields
        edit.name = main_category_name
        edit.descriptions = description 
        edit.img = image
        
        # Save updated data
        edit.save()

        return redirect('dashboard_app:main_category')

    return render(request, "dashboard/update_main_category.html", {"data": data})


@login_required(login_url='dashboard_app:dashboard_login')
def delete_main_category(request,id):
    data = Main_Category.objects.get(id=id) 
    data.delete()  
    return redirect('main_category')
 
#############################################################################################
       # Product Section, contains "all_products, add, update and delete product" #
#############################################################################################


@login_required(login_url='dashboard_app:dashboard_login')
def all_products(request):
    data = Product.objects.all()
    return render(request, "dashboard/all_products.html", {"data": data})


@login_required(login_url='dashboard_app:dashboard_login')
def add_product(request):
    data = Main_Category.objects.all() 
    if request.method == 'POST':
        # Extracting data from the POST request
        brand = request.POST['brand']
        model = request.POST['model']
        price = request.POST['price']
        description = request.POST['description']
        color = request.POST['color']
        display_size = request.POST['display_size']
        camera = request.POST['camera']
        storage = request.POST['storage']
        ram = request.POST['ram']
        network = request.POST.get('network', False) == 'true'
        smart = request.POST.get('smart', False) == 'true'
        battery = request.POST['battery']
        image = request.FILES.get('image')
        stock = request.POST['stock']
        offer = request.POST['offer']
        delete = request.POST.get('delete', False) == 'True'
        main_category_id = request.POST.get('main_category_id')  

        main_cat = Main_Category.objects.get(id=main_category_id)
        
        query = Product.objects.create(
            brand=brand,
            model=model,
            price=price,
            description=description,
            color=color,
            display_size=display_size,
            camera=camera,
            storage=storage,
            ram=ram,
            network=network,
            smart=smart,
            battery=battery,
            image=image,
            stock=stock,
            offer=offer,
            deleted=delete,
            main_category=main_cat  # Associate the Product with a main_category
        )
        query.save()
        return redirect('dashboard_app:all_products')
    # Render the form if it's not a POST request
    return render(request, 'dashboard/add_product.html', {"data": data})


@login_required(login_url='dashboard_app:dashboard_login')
def update_product(request, id):
    data = Main_Category.objects.all()
    product = Product.objects.get(id=id)
    network = request.POST.get('network')
    smart = request.POST.get('smart')
    delete = request.POST.get('')
    if request.method == 'POST':
        brand = request.POST['brand']
        model = request.POST['model']
        price = request.POST['price']
        description = request.POST['description']
        color = request.POST['color']
        display_size = request.POST['display_size']
        camera = request.POST['camera']
        storage = request.POST['storage']
        ram = request.POST['ram']
        network = request.POST.get('network', False)
        smart = request.POST.get('smart', False)
        battery = request.POST['battery']
        image = request.FILES.get('image')
        stock = request.POST['stock']
        offer = request.POST['offer']
        delete = request.POST.get('delete', False)

        # Retrieve existing data
        edit = Product.objects.get(id=id)
        # Update data in the table
        edit.brand = brand
        edit.model=model
        edit.price=price
        edit.description=description
        edit.color=color
        edit.display_size=display_size
        edit.camera=camera
        edit.storage=storage
        edit.ram=ram
        edit.network=network
        edit.smart=smart
        edit.battery=battery
        edit.image=image
        edit.stock=stock
        edit.offer=offer
        edit.deleted=delete
        edit.save()

        return redirect('dashboard_app:all_products')
    return render(request, "dashboard/update_product.html", {"product": product, "data" : data})


@login_required(login_url='dashboard_app:dashboard_login')
def delete_product(request,id):
    data = Product.objects.get(id=id) 
    data.delete()  
    return redirect('dashboard_app:all_products')
        






