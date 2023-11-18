from django.shortcuts import render
from django.http import HttpResponse
from main_app.models import Main_Category

# Create your views here.
def home(request):
    return render(request,'dashboard/all_products.html')

def main_category(request):
    main_category = Main_Category.objects.all()
    


    return render(request,"dashboard/main_category.html",{'main_category': main_category})

        