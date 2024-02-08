from django import forms
from django.contrib.auth.forms import UserCreationForm
from gauth_app.models import Customer, Address


# Create your forms here.

class NewUserForm(UserCreationForm):
	email = forms.EmailField(required=True)

	class Meta:
		model = Customer
		fields = ("email", "password1", "password2")

	def save(self, commit=True):
		user = super(NewUserForm, self).save(commit=False)
		user.email = self.cleaned_data['email']
		if commit:
			user.save()
		return user


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ['first_name', 'last_name', 'phone']

    def clean_first_name(self):
        first_name = self.cleaned_data.get('first_name')
        
        # Check if first name contains only white spaces or numbers
        if not first_name.strip() or any(char.isdigit() for char in first_name):
            raise forms.ValidationError("First name cannot be empty or contain numbers.")

        return first_name

    def clean_last_name(self):
        last_name = self.cleaned_data.get('last_name')
        
        # Check if last name contains only white spaces or numbers
        if not last_name.strip() or any(char.isdigit() for char in last_name):
            raise forms.ValidationError("Last name cannot be empty or contain numbers.")

        return last_name

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        
        # Check if phone number is all zeros
        if phone and phone.strip('0') == '':
            raise forms.ValidationError("Phone number cannot be all zeros.")
        
        # Check if phone number is exactly 10 digits long
        if phone and len(phone) != 10:
            raise forms.ValidationError("Phone number must be exactly 10 digits long.")

        return phone




class AddressForm(forms.ModelForm):
    class Meta:
        model = Address
        fields = ['address_name', 'first_name', 'last_name', 'email', 'phone', 'address_1', 'address_2', 'country', 'state', 'city', 'pin']