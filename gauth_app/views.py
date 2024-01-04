from django.contrib.auth import login, authenticate, logout 
from django.shortcuts import render, redirect
from .forms import NewUserForm
from gauth_app.models import Address
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required


#############################################################################################
                              # User Login related views #
#############################################################################################

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
                    return redirect("main_app:home", {'messages': messages.get_messages(request)})
            else:
                messages.error(request, "Invalid username or password. Please check your credentials.")
        else:
            messages.error(request, "Invalid form submission. Please check your input.")
    else:
        form = AuthenticationForm()

    return render(request=request, template_name="main/login.html", context={"login_form": form})


def user_logout(request):
    logout(request)
    return redirect('gauth_app:user_login')


#############################################################################################
                            # User Profile and address management #
#############################################################################################


def profile(request):
    customer = request.user
    default_address = Address.objects.filter(user=customer, default=True).first()
    return render(request, 'main/profile.html', {'customer': customer, 'default_address': default_address})


def address(request):
    data = Address.objects.all()
    return render(request, 'main/address.html', {'data': data})


def add_address(request):
    if request.method == 'POST':
        user = request.user
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

        query = Address.objects.create(
            user = user,
            default = default,
            address_name = address_name,
            first_name = first_name,
            last_name = last_name,
            address_1 = address_1,
            address_2 = address_2,
            country = country,
            state = state,
            city = city,
            phone = phone,
            email = email,
            pin = pin,
        )
        query.save()
        return redirect('gauth_app:address')
    return render(request, 'main/add_address.html')

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


def delete_address(request,id):
    data = Address.objects.get(id=id) 
    data.delete()  
    return redirect('gauth_app:address')