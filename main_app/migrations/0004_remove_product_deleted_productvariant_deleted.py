# Generated by Django 4.2.7 on 2024-02-06 04:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main_app', '0003_remove_product_storage_productvariant_storage'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='product',
            name='deleted',
        ),
        migrations.AddField(
            model_name='productvariant',
            name='deleted',
            field=models.BooleanField(default=False),
        ),
    ]
