from django.shortcuts import render,redirect, get_object_or_404
from django.http import HttpResponse
from django.views.decorators.cache import cache_control,never_cache
from main_app.models import Main_Category,Smartphone,Featurephone, Gadget

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
        print(edit)

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
    smartphones = Smartphone.objects.all()
    featurephones = Featurephone.objects.all()
    # Combine the QuerySets using union
    data = smartphones.union(featurephones)
    return render(request, "dashboard/all_products.html", {"data": data})

        
def add_product(request):
    if request.method == 'POST':
        phone_category = request.POST.get('phone_category')

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

        # Get or create the Main_Category instance
        main_category_name = request.POST.get('main_category_name', '')
        main_category, created = Main_Category.objects.get_or_create(name=main_category_name, descriptions='', img='null')  

        # Saving Data to the database based on the category
        if phone_category == 'smartphone':
            query1 = Smartphone.objects.create(
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
                main_category=main_category  # Associate the Smartphone with a main_category
            )
            query1.save()
        else:
            query2 = Featurephone.objects.create(
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
                main_category=main_category  # Associate the Featurephone with a main_category
            )
            query2.save()

        return redirect('all_products')

    return render(request, 'dashboard/add_product.html')



def update_product(request, id):
    try:
        # Try to get the product instance as a Smartphone
        product = get_object_or_404(Smartphone, id=id)
    except Smartphone.DoesNotExist:
        try:
            # If not found as a Smartphone, try to get it as a Featurephone
            product = get_object_or_404(Featurephone, id=id)
        except Featurephone.DoesNotExist:
            # If not found as a Featurephone either, return a 404 response
            raise Http404("Product does not exist")
        
    # product = Smartphone.objects.filter(id=id).first()

    if request.method == 'POST':
        # Retrieve common fields for both smartphone and feature phone
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

        # Update common fields
        product.brand = brand
        product.model = model
        product.price = price
        product.description = description
        product.color = color
        product.display_size = display_size
        product.camera = camera
        product.storage = storage
        product.ram = ram
        product.network = network
        product.smart = smart
        product.battery = battery
        product.image = image
        product.stock = stock
        product.offer = offer
        product.deleted = delete

        # Update main category (create if not exists)
        main_category_name = request.POST.get('main_category_name', '')
        main_category, created = Main_Category.objects.get_or_create(name=main_category_name, descriptions='', img='null')
        product.main_category = main_category

        # Update type-specific fields for Smartphone or Featurephone
        if isinstance(product, Smartphone):
            # Update Smartphone-specific fields
            # Add your smartphone-specific fields update here
            pass
        elif isinstance(product, Featurephone):
            # Update Featurephone-specific fields
            # Add your featurephone-specific fields update here
            pass

        # Save the updated product
        product.save()

        return redirect('all_products')

    return render(request, "dashboard/update_product.html", {"product": product})