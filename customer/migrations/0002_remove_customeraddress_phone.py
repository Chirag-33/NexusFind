# Generated by Django 5.2 on 2025-04-16 07:56

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('customer', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='customeraddress',
            name='phone',
        ),
    ]
