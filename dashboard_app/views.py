from django.shortcuts import render,redirect
from main_app.models import Main_Category, Product
from django.shortcuts import get_object_or_404

# Create your views here.
def dashboard_home(request):
    return render(request,'dashboard/home.html')

#############################################################################################
            # Main Category Section, All product, Add, update and delete
#############################################################################################

def main_category(request):
    data = Main_Category.objects.all()
    return render(request,"dashboard/main_category.html",{"data": data})

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

        return redirect('main_category')

    return render(request, "dashboard/update_main_category.html", {"data": data})

def delete_main_category(request,id):
    data = Main_Category.objects.get(id=id) 
    data.delete()  
    return redirect('main_category')
 
#############################################################################################
       # Product Section, contains "all_products, add, update and delete product"
#############################################################################################


def all_products(request):
    data = Product.objects.all()
    return render(request, "dashboard/all_products.html", {"data": data})

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
        return redirect('all_products')
    # Render the form if it's not a POST request
    return render(request, 'dashboard/add_product.html', {"data": data})

def update_product(request, id):
    data = Main_Category.objects.all()
    product = Product.objects.get(id=id)

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
        network = request.POST.get('network', False) == 'true'
        smart = request.POST.get('smart', False) == 'true'
        battery = request.POST['battery']
        image = request.FILES.get('image')
        stock = request.POST['stock']
        offer = request.POST['offer']
        delete = request.POST.get('delete', False) == 'True'

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

        return redirect('all_products')
    return render(request, "dashboard/update_product.html", {"product": product, "data" : data})

def delete_product(request,id):
    data = Product.objects.get(id=id) 
    data.delete()  
    return redirect('all_products')
        






