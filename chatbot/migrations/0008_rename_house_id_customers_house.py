# Generated by Django 4.2.10 on 2024-02-13 20:20

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('chatbot', '0007_rename_house_customers_house_id'),
    ]

    operations = [
        migrations.RenameField(
            model_name='customers',
            old_name='house_id',
            new_name='house',
        ),
    ]
