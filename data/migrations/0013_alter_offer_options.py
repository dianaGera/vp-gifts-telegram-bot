# Generated by Django 4.1.5 on 2023-01-18 12:44

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('data', '0012_alter_category_options_alter_subcategory_options_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='offer',
            options={'ordering': ['-created_at']},
        ),
    ]
