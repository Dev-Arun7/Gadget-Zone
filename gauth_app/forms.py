from django import forms 
# from django.contrib.auth import forms
from gauth_app.models import CustomUser


class SignupForm(forms.ModelForm):
    password2 = forms.CharField(max_length=220, widget=forms.PasswordInput)

    class Meta:
        model = CustomUser
        fields = ['email', 'password', 'password2']

    def clean(self):
        cleaned_data = super().clean()
        print(cleaned_data)
        password = cleaned_data.pop('password')
        password2 = cleaned_data.get('password2')
        
        # Check if passwords match
        if password and password2 and password != password2:
            raise forms.ValidationError("Passwords do not match. Please enter them again.")
        
        return cleaned_data

class LoginForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['email', 'password']