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


class Product(models.Model):
    main_category = models.ForeignKey(Main_Category, on_delete=models.CASCADE)
    brand = models.CharField(max_length=50)
    model = models.CharField(max_length=100)
    price = models.IntegerField()
    description = models.TextField()
    color = models.CharField(max_length=10)
    display_size = models.IntegerField()
    camera = models.CharField(max_length=20)
    storage = models.CharField(max_length=20)
    ram = models.CharField(max_length=10)
    network = models.BooleanField()
    smart = models.BooleanField()
    battery = models.IntegerField()
    image = models.ImageField(upload_to='products',
                              default='default_image.jpg')
    stock = models.IntegerField(default=3)
    offer = models.PositiveBigIntegerField(default=0, null=True, blank=True)
    offer_price = models.IntegerField(null=True, blank=True)
    deleted = models.BooleanField(default=False)
    objects = models.Manager()

    def __str__(self):
            return f"{self.brand} {self.model}"

    @staticmethod
    def search_by_model(query):
        return Product.objects.filter(model__icontains=query)


class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='additional_images')
    image = models.ImageField(upload_to='product_images', blank=True, null=True)
    objects = models.Manager()
    def __str__(self):
        return f"Image for {self.product.model}"

