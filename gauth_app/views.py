from django.shortcuts import render

# Create your views here.
def signup(request):
    return render(request,'main/signup.html')

def login(request):
    return render(request,'main/login.html')

