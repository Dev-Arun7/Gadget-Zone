from django.shortcuts import render,redirect
from django.http import HttpResponse
from django.views.decorators.cache import cache_control,never_cache
from main_app.models import Main_Category

# Create your views here.
def home(request):
    return render(request,'dashboard/all_products.html')

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
 