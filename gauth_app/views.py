from django.contrib.auth import login, authenticate, logout 
from django.views.decorators.cache import never_cache
from django.shortcuts import render, redirect, get_object_or_404
from .forms import NewUserForm
from gauth_app.models import Address, Customer, Wallet
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from .forms import ProfileForm, AddressForm
from django.db import transaction
import random
import string


#############################################################################################
                              # User Login related views #
#############################################################################################


def generate_referral_code(length=8):
    letters = string.ascii_letters
    code = ''.join(random.choice(letters) for _ in range(length))
    return code



@never_cache
def user_signup(request):
    if request.method == "POST":
        form = NewUserForm(request.POST)
        if form.is_valid():
            referral_code = form.cleaned_data.get('referral')
            if referral_code:
                try:
                    referrer = Customer.objects.get(referral=referral_code)
                except Customer.DoesNotExist:
                    messages.error(request, "Invalid referral code. Please try again.")
                    return redirect("gauth_app:user_signup")

            with transaction.atomic():
                new_customer = form.save(commit=False)
                new_customer.username = form.cleaned_data['email']

                # Save the new customer
                new_customer.save()

                if referral_code:
                    # Create a wallet for the new customer if it doesn't exist
                    new_wallet, created = Wallet.objects.get_or_create(user=new_customer)
                    referrer_wallet, created = Wallet.objects.get_or_create(user=referrer)
                    referrer_wallet.balance += 100
                    referrer_wallet.save()
                    new_wallet.balance += 100
                    new_wallet.save()

                # Generate a unique referral code
                new_customer.referral = generate_referral_code()
                new_customer.save()

                # Authenticate the user before login just after signup
                user = authenticate(request, username=new_customer.username, password=form.cleaned_data['password1'])
                login(request, user, backend='django.contrib.auth.backends.ModelBackend') 

                messages.success(request, "Registration successful.")
                return redirect("main_app:home")
        else:
            messages.error(request, "Unsuccessful registration. Invalid information.")
    else:
        form = NewUserForm()
    return render(request=request, template_name="main/signup.html", context={"register_form": form})


@never_cache
def user_login(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)

            if user:
                if user.is_blocked:
                    # Display a message for blocked users
                    messages.error(request, "Your account is blocked. Please contact support for assistance.")
                    return render(request, 'main/blocked.html')
                else:
                    login(request, user)
                    messages.success(request, f"Welcome back, {username}!")
                    return redirect("main_app:home")
            else:
                messages.error(request, "Invalid username or password. Please check your credentials.")
        else:
            messages.error(request, "Invalid form submission. Please check your input.")
    else:
        form = AuthenticationForm()

    return render(request=request, template_name="main/login.html", context={"login_form": form})


@never_cache
def user_logout(request):
    logout(request)
    return redirect('gauth_app:user_login')


#############################################################################################
                            # User Profile and address management #
#############################################################################################

@login_required
def profile(request):
    customer = request.user
    return render(request, 'main/profile.html', {'customer': customer})


@login_required
def manage_profile(request):
    if request.method == 'POST':
        form = ProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()  # Save the updated user instance
            return redirect('gauth_app:profile')
    else:
        form = ProfileForm(instance=request.user)  # Populate form with current user data

    return render(request, 'main/manage_profile.html', {'form': form})


@login_required
def address(request):
    current_user = request.user
    data = Address.objects.filter(user=current_user)
    
    return render(request, 'main/address.html', {'data': data})


@login_required
def add_address(request, redirect_page):
    if request.method == 'POST':
        form = AddressForm(request.POST)
        if form.is_valid():
            new_address = form.save(commit=False)
            new_address.user = request.user
            new_address.default = request.POST.get('default', False) == 'True'
            new_address.save()

            if redirect_page == 'all_addresses':
                return redirect('gauth_app:address')
            elif redirect_page == 'checkout':
                return redirect('main_app:checkout')
    else:
        form = AddressForm()

    return render(request, 'main/add_address.html', {'form': form, 'redirect_page': redirect_page})


@login_required
def update_address(request, id):
    # Retrieve the specific address object by its ID
    address = get_object_or_404(Address, id=id)

    if request.method == 'POST':
        # Populate the form with the POST data and the instance of the address to be edited
        form = AddressForm(request.POST, instance=address)
        if form.is_valid():
            # Save the updated address details
            form.save()
            return redirect('gauth_app:address')
    else:
        # If it's a GET request, populate the form with the existing address details
        form = AddressForm(instance=address)

    # Render the update address form template with the form and address data
    context = {
        'form': form,
        'address': address,
    }
    return render(request, 'main/update_address.html', context)


@login_required
def delete_address(request,id):
    data = Address.objects.get(id=id) 
    data.delete()  
    return redirect('gauth_app:address')