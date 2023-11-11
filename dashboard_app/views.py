from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.
def home(request):
    return render(request,'dashboard/all_products.html')

def all_products(request):
    return render(request,'dashboard/brands.html')
