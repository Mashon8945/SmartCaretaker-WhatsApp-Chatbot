# Generated by Django 3.2.16 on 2024-03-18 14:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chatbot', '0026_customerstate'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customerstate',
            name='phone',
            field=models.CharField(max_length=30, unique=True),
        ),
    ]