# Generated by Django 4.2.7 on 2024-01-03 12:51

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('gauth_app', '0013_cart_total'),
    ]

    operations = [
        migrations.AddField(
            model_name='cart',
            name='created_at',
            field=models.DateTimeField(blank=True, default=django.utils.timezone.now),
        ),
    ]
