from django.contrib.auth import login, authenticate, logout 
from django.views.decorators.cache import never_cache
from django.shortcuts import render, redirect
from .forms import NewUserForm
from gauth_app.models import Address, Customer
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from .forms import ProfileForm, AddressForm


#############################################################################################
                              # User Login related views #
#############################################################################################


@never_cache
def user_signup(request):
    if request.method == "POST":
        form = NewUserForm(request.POST)
        if form.is_valid():
            new_customer = form.save(commit=False)
            new_customer.username = form.cleaned_data['email']
            new_customer.save()

            # Authenticate the user before login just after signup
            user = authenticate(request, username=new_customer.username, password=form.cleaned_data['password1'])
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')  # Specify the authentication backend

            messages.success(request, "Registration successful.")
            return redirect("gauth_app:user_login")
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
    default_address = Address.objects.filter(user=customer, default=True).first()
    return render(request, 'main/profile.html', {'customer': customer, 'default_address': default_address})


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
    data = Address.objects.all()
    address = Address.objects.get(id = id)
    default = request.POST.get('default')
    if request.method == 'POST':
        default = request.POST.get('default', False) == 'True'
        address_name = request.POST['address_name']
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        address_1 = request.POST['address_1']
        address_2 = request.POST['address_2']
        country = request.POST['country']
        state = request.POST['state']
        city = request.POST['city']
        phone = request.POST['phone']
        email = request.POST['email']
        pin = request.POST['pin']

        # Retrieve existing data
        edit = Address.objects.get(id = id)
        # Update data in the table
        edit.default = default
        edit.address_name = address_name
        edit.first_name = first_name
        edit.last_name = last_name
        edit.address_1 = address_1
        edit.address_2 = address_2
        edit.country = country
        edit.state = state
        edit.city = city
        edit.phone = phone
        edit.email = email
        edit.pin = pin
        edit.save()
        
        return redirect('gauth_app:address')
    context = {
           "address": address,
            "data" : data
            }

    return render(request, 'main/update_address.html', context)



@login_required
def delete_address(request,id):
    data = Address.objects.get(id=id) 
    data.delete()  
    return redirect('gauth_app:address')