# Generated by Django 3.2.16 on 2024-03-24 13:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chatbot', '0030_alter_whatsappmessage_body'),
    ]

    operations = [
        migrations.AlterField(
            model_name='whatsappmessage',
            name='body',
            field=models.CharField(blank=True, max_length=10000, null=True),
        ),
    ]
