# Generated by Django 4.1.5 on 2023-01-24 13:44

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('data', '0032_paymentstatus_ru_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='giftorder',
            name='payment_address',
            field=models.ForeignKey(db_column='payment_address_id', null=True, on_delete=django.db.models.deletion.SET_NULL, to='data.paymentaddress'),
        ),
        migrations.AlterField(
            model_name='paymentstatus',
            name='name',
            field=models.CharField(max_length=128, unique=True),
        ),
    ]
