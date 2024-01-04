from django.db import models
from django.contrib.auth.models import AbstractUser
# from .manager import UserManager
from datetime import date
from django.utils import timezone
from main_app.models import *
# Create your models here.


class Customer(AbstractUser):
    email = models.EmailField(unique=True)
    username = models.CharField(unique=True, null=True, blank=True, max_length=20)
    phone = models.CharField(max_length=10)
    is_verified = models.BooleanField(default=False)
    email_token = models.CharField(max_length=100, null=True, blank=True)
    forgot_password = models.CharField(max_length=100, null=True, blank=True)
    last_login_time = models.DateTimeField(default=timezone.now, null=True, blank=True)
    last_logout_time = models.DateTimeField(default=timezone.now, null=True, blank=True)
    profile_photo = models.ImageField(upload_to='profile_photo', null=True, blank=True, default='profile.png')
    wallet_bal = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    is_blocked = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def save(self, *args, **kwargs):
        # Truncate the username (email) if it's longer than 20 characters
        if self.email and len(self.email) > 20:
            self.username = self.email[:20]
        else:
            self.username = self.email

        super().save(*args, **kwargs)

    def __str__(self):
        return self.email
       
class Address(models.Model):
    user              = models.ForeignKey(Customer,on_delete=models.CASCADE)
    address_name      = models.CharField(max_length=50, null=False, blank=True)
    first_name        = models.CharField(max_length=50, null=False, blank=True)
    last_name         = models.CharField(max_length=50, null=False,blank=True)
    email             = models.EmailField()
    phone             = models.BigIntegerField(blank=True)
    address_1         = models.CharField(max_length=250, blank=True)
    address_2         = models.CharField(max_length=250, blank=True)
    country           = models.CharField(max_length=15)
    state             = models.CharField(max_length=15)
    city              = models.CharField(max_length=15)
    pin               = models.IntegerField()
    is_deleted        = models.BooleanField(default=False)
    default           = models.BooleanField(default=False)
    objects = models.Manager()
    def __str__(self):
        return f"{self.address_name} "
  

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
    user              = models.ForeignKey(Customer, on_delete=models.CASCADE) 
    address           = models.ForeignKey(Address, on_delete=models.SET_NULL,null=True,blank=True)
    product           = models.ForeignKey(Product, on_delete=models.CASCADE, null=True, blank=True)
    amount            = models.CharField(max_length=100)  
    payment_type      = models.CharField(max_length=100)  
    status            = models.CharField(max_length=100, choices=ORDER_STATUS, default='pending' )  
    quantity          = models.IntegerField(default=0, null=True, blank=True)
    image             = models.ImageField(upload_to='products', null=True, blank=True)
    date              = models.DateField(default=date.today) 
            
    def __str__(self):
        return f"Order #{self.pk} - {self.product}"


class Cart(models.Model):
    user = models.ForeignKey(Customer, on_delete = models.CASCADE, null=True, blank=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, null=True, blank=True)
    quantity = models.IntegerField(default=0)
    image = models.ImageField(upload_to="products", null=True, blank=True)
    total = models.IntegerField(default=0)
    created_at = models.DateTimeField(default=timezone.now, blank=True)
    objects = models.Manager()

    def __str__(self) -> str:
        return f"Cart - {self.user} - {self.product} - Quantity: {self.quantity}"

class Wishlist(models.Model):
    user = models.ForeignKey(Customer, on_delete = models.CASCADE, null=True, blank=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, null=True, blank=True)
    image = models.ImageField(upload_to="products", null=True, blank=True)
    objects = models.Manager()
    
    def __str__(self) -> str:
        return f"Wishlist - {self.user} - {self.product}"