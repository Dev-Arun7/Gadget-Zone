from django.db import models

# Create your models here.


class Main_Category(models.Model):
    name = models.CharField(max_length=100)
    descriptions = models.TextField(default='Default Description')
    img = models.ImageField(upload_to='categories', default='null', null=True, blank=True)
    deleted = models.BooleanField(default=False)
    objects = models.Manager()

    def __str__(self):
        return str(self.name)


class Brand(models.Model):
    name = models.CharField(max_length=50)
    image = models.ImageField(upload_to='products', null=True, blank=True)
    description = models.TextField()
    deleted = models.BooleanField(default=False)
    objects = models.Manager()

    def __str__(self):
        return self.name


class Product(models.Model):
    main_category = models.ForeignKey(Main_Category, on_delete=models.CASCADE)
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE)
    model = models.CharField(max_length=100)
    description = models.TextField()
    color = models.CharField(max_length=10)
    display_size = models.IntegerField()
    camera = models.CharField(max_length=20, null=True, blank=True)
    network = models.BooleanField()
    smart = models.BooleanField()
    battery = models.IntegerField(null=True, blank=True)
    image = models.ImageField(upload_to='products',
                              default='default_image.jpg')
    objects = models.Manager()

    def __str__(self):
        return self.model

    @staticmethod
    def search_by_model(query):
        return Product.objects.filter(model__icontains=query)
    

class ProductVariant(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    ram = models.CharField(max_length=10)
    storage = models.CharField(max_length=20, null=True)
    price = models.IntegerField()
    stock = models.IntegerField(default=3)
    offer = models.PositiveBigIntegerField(default=0, null=True, blank=True)
    offer_price = models.IntegerField(null=True, blank=True)
    deleted = models.BooleanField(default=False)
    objects = models.Manager()

    def __str__(self):
        return f"{self.product} - {self.ram} RAM" 



class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='additional_images')
    image = models.ImageField(upload_to='product_images', blank=True, null=True)
    objects = models.Manager()
    def __str__(self):
        return f"Image for {self.product.model}"

    def toggle_deleted(self):
        self.deleted = not self.deleted
        self.save()


 