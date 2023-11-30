

from django.db import models
from django.contrib.auth.models import AbstractBaseUser
from datetime import date,datetime
from main_app.models import *
# Create your models here.

class Customer(models.Model):
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=30, null=True)
    last_name = models.CharField(max_length=30, null=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add = True)
    phone=models.CharField(max_length=15,null=True)
    wallet_bal = models.IntegerField(default=0)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def __str__(self):
        full_name = f"{self.first_name} {self.last_name}"
        return full_name.strip()
    
class Address(models.Model):
    user = models.ForeignKey(Customer,on_delete=models.CASCADE)
    first_name = models.CharField(max_length=50, null=False, blank=True)
    last_name = models.CharField(max_length=50, null=False,blank=True)
    email = models.EmailField()
    number = models.BigIntegerField(blank=True)
    address = models.CharField(max_length=250)
    country = models.CharField(max_length=15)
    state = models.CharField(max_length=15)
    city = models.CharField(max_length=15)
    pin_code = models.IntegerField()
    is_deleted = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.first_name} {self.last_name}, {self.address}, {self.city}, {self.state} - {self.user}"
  
class Order(models.Model):

    ORDER_STATUS = (
        ('pending', 'Pending'),
        ('processing','processing'),
        ('shipped','shipped'),
        ('delivered','delivered'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('refunded','refunded'),
        ('on_hold','on_hold')
    )
    user           =   models.ForeignKey(Customer, on_delete=models.CASCADE) 
    address        =   models.ForeignKey(Address, on_delete=models.SET_NULL,null=True,blank=True)
    product        =   models.ForeignKey(Product, on_delete=models.CASCADE, null=True, blank=True)
    amount         =   models.CharField(max_length=100)  
    payment_type   =   models.CharField(max_length=100)  
    status         =   models.CharField(max_length=100, choices=ORDER_STATUS, default='pending' )  
    quantity       =   models.IntegerField(default=0, null=True, blank=True)
    image          =   models.ImageField(upload_to='products', null=True, blank=True)
    date           =   models.DateField(default=date.today) 
         
    def __str__(self):
        return f"Order #{self.pk} - {self.product}"



