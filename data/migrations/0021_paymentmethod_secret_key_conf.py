# Generated by Django 4.1.5 on 2023-01-19 15:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('data', '0020_alter_giftorder_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='paymentmethod',
            name='secret_key_conf',
            field=models.CharField(blank=True, max_length=128, null=True),
        ),
    ]
