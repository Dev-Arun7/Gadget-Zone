# Generated by Django 4.2.7 on 2024-02-15 07:20

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('gauth_app', '0004_rename_offer_total_order_details_offer_price_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='order_details',
            old_name='quntity',
            new_name='quantity',
        ),
    ]