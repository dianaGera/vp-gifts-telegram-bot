# Generated by Django 4.1.5 on 2023-01-24 18:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('data', '0035_alter_payment_txid_alter_payment_address_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='tguser',
            name='chat_id',
            field=models.IntegerField(null=True),
        ),
    ]
