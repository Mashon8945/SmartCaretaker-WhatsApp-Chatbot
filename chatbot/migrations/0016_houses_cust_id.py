# Generated by Django 4.2.10 on 2024-02-22 16:42

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('chatbot', '0015_remove_houses_customer_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='houses',
            name='cust_id',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='chatbot.customers'),
        ),
    ]
