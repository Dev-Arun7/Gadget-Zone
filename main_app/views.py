from django.shortcuts import render
from django.http import HttpResponse
from main_app.models import Main_Category

# Create your views here.
def home(request):
    return render(request,'main/home.html')


def signup(request):
    return render(request,'main/signup.html')

def base(request):
    return render(request,'main/base.html')
