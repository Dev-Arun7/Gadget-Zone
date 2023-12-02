from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout 
from .forms import SignupForm, LoginForm


# Create your views here.

# signup page
def user_signup(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)
        print(form)
        if form.is_valid():
            form.save()
            return redirect('user_login')
    else:
        form = SignupForm()
    return render(request, 'main/signup.html', {'form': form})

# login page
# def user_login(request):
#     if request.method == 'POST':
#         form = LoginForm(request.POST)
#         if form.is_valid():
#             email = form.cleaned_data['email']
#             password = form.cleaned_data['password']
#             user = authenticate(request, email=email, password=password)
#             if user:
#                 login(request, user)    
#                 return redirect('main_app:home')
#     else:
#         form = LoginForm()
#     return render(request, 'main/login.html', {'form': form})

def user_login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            pass
        else:
            email = form.cleaned_data.get('email')
            password = form.cleaned_data.get('password')
            user = authenticate(request, email=email, password=password)
            print(user,'555555555555555555555555555555555555555')
            if user:
                login(request, user)      
            return redirect('main_app:home')
    else:
        form = LoginForm()
    return render(request, 'main/login.html', {'form': form})

# logout page
def user_logout(request):
    logout(request)
    return redirect('gauth_app:user_login')