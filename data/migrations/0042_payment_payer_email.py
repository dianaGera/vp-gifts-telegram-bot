# Generated by Django 4.1.5 on 2023-02-01 16:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('data', '0041_alter_payment_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='payment',
            name='payer_email',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]