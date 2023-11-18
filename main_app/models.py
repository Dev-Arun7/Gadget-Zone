from django.db import models

# Create your models here.
class Main_Category(models.Model):
    name = models.CharField(max_length=100)
    descriptions = models.TextField(default='Default Description')
    img = models.ImageField(upload_to='categories', default='null')
    objects = models.Manager()
    def __str__(self):
        return str(self.name)
    
class Category(models.Model):
    main_category = models.ForeignKey(Main_Category,on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    objects = models.Manager()
    def __str__(self):
        return str(self.name) + "--" + str(self.main_category)
    





