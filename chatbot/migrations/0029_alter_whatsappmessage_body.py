# Generated by Django 3.2.16 on 2024-03-24 12:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chatbot', '0028_adminmessage'),
    ]

    operations = [
        migrations.AlterField(
            model_name='whatsappmessage',
            name='body',
            field=models.CharField(blank=True, max_length=500, null=True),
        ),
    ]
