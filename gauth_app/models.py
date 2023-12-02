from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from datetime import date,datetime
from main_app.models import Product
# Create your models here.



class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        return self.create_user(email, password, **extra_fields)

class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', null=True, blank=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    

    objects = CustomUserManager()
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    
class Address(models.Model):
    user = models.ForeignKey(CustomUser,on_delete=models.CASCADE)
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
    user           =   models.ForeignKey(CustomUser, on_delete=models.CASCADE) 
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



