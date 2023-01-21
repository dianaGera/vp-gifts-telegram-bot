# Generated by Django 4.1.5 on 2023-01-20 15:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('data', '0024_alter_currencydetail_country'),
    ]

    operations = [
        migrations.AddField(
            model_name='payment',
            name='TxID',
            field=models.CharField(max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='payment',
            name='_type',
            field=models.CharField(choices=[('deposit', 'Deposit'), ('withdraw', 'Withdraw')], default='deposit', max_length=255),
        ),
        migrations.AddField(
            model_name='payment',
            name='bc_id',
            field=models.CharField(max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='payment',
            name='insert_time',
            field=models.CharField(default=1, max_length=255),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='payment',
            name='status',
            field=models.BooleanField(default=True, null=True),
        ),
    ]