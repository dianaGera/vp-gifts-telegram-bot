# Generated by Django 4.1.5 on 2023-01-13 18:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('data', '0004_alter_tguser_currency'),
    ]

    operations = [
        migrations.AddField(
            model_name='offer',
            name='description',
            field=models.TextField(blank=True, null=True),
        ),
    ]
