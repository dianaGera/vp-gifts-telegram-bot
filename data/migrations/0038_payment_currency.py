# Generated by Django 4.1.5 on 2023-01-24 19:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('data', '0037_payment_fiat_amount'),
    ]

    operations = [
        migrations.AddField(
            model_name='payment',
            name='currency',
            field=models.CharField(max_length=255, null=True),
        ),
    ]