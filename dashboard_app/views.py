from django.shortcuts import render
from django.http import HttpResponse
from .models import Main_category

# Create your views here.
def home(request):
    return render(request,'dashboard/all_products.html')

def main_category(request):
    cat1 = Main_category()
    cat1.name = 'Smartphones'
    cat1.desc = 'The world is in your hand'

    cat2 = Main_category()
    cat2.name = 'Rugged Phones'
    cat2.desc = 'Tough devices'

    cat3 = Main_category()
    cat3.name = 'Others'
    cat3.desc = 'All other phones'

    cat4 = Main_category()
    cat4.name = 'Others'
    cat4.desc = 'All other phones'

    cats = [cat1, cat2, cat3, cat4]



    return render(request,"dashboard/main_category.html",{'cat': cats})

       