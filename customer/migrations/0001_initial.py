# Generated by Django 5.2 on 2025-04-15 13:17

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='CustomerAddress',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('phone', models.IntegerField()),
                ('email', models.EmailField(max_length=254, unique=True)),
                ('address_line_1', models.CharField(max_length=100, null=True)),
                ('address_line_2', models.CharField(blank=True, max_length=100, null=True)),
                ('address_type', models.CharField(choices=[('H', 'Home'), ('B', 'Work'), ('O', 'Other')], max_length=10)),
                ('city', models.CharField(max_length=50)),
                ('state', models.CharField(max_length=50)),
                ('country', models.CharField(max_length=50)),
                ('pincode', models.CharField(max_length=6)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='addresses', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Customer Address',
                'verbose_name_plural': 'Customer Addresses',
            },
        ),
    ]
