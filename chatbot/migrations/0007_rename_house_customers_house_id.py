# Generated by Django 4.2.10 on 2024-02-13 20:17

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('chatbot', '0006_complaints_complaint'),
    ]

    operations = [
        migrations.RenameField(
            model_name='customers',
            old_name='house',
            new_name='house_id',
        ),
    ]
