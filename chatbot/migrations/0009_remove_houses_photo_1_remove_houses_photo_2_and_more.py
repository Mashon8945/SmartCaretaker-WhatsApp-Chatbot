# Generated by Django 4.2.10 on 2024-02-14 18:50

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('chatbot', '0008_rename_house_id_customers_house'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='houses',
            name='photo_1',
        ),
        migrations.RemoveField(
            model_name='houses',
            name='photo_2',
        ),
        migrations.RemoveField(
            model_name='houses',
            name='photo_3',
        ),
        migrations.RemoveField(
            model_name='houses',
            name='photo_4',
        ),
    ]
