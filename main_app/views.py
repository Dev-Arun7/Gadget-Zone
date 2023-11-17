from django.shortcuts import render
from django.http import HttpResponse
from main_app.models import Main_Category,Category

# Create your views here.
def home(request):
    category = Category.objects.all().order_by('-id')
    print(category)
    context = {
        'category' : category,
    }
    return render(request,'main/home.html',context)

def all_products(request):
    return render(request,'product_list/register.html')

def signup(request):
    return render(request,'main/signup.html')

def base(request):
    return render(request,'main/base.html')
