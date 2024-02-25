# Generated by Django 4.2.10 on 2024-02-22 16:47

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('chatbot', '0017_alter_houses_cust_id'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='houses',
            name='cust_id',
        ),
        migrations.AddField(
            model_name='houses',
            name='customer',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='chatbot.customers'),
        ),
    ]
