# Generated by Django 4.1.5 on 2023-01-19 17:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('data', '0022_currencydetail_type_payment'),
    ]

    operations = [
        migrations.AlterField(
            model_name='currencydetail',
            name='code',
            field=models.CharField(max_length=10, unique=True),
        ),
    ]
