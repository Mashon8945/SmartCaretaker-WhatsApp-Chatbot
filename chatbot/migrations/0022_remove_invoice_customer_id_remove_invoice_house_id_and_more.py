# Generated by Django 4.2.9 on 2024-03-05 16:02

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('chatbot', '0021_alter_assignment_house_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='invoice',
            name='customer_id',
        ),
        migrations.RemoveField(
            model_name='invoice',
            name='house_id',
        ),
        migrations.RemoveField(
            model_name='invoice',
            name='total',
        ),
        migrations.RemoveField(
            model_name='transactions',
            name='house_id',
        ),
        migrations.AddField(
            model_name='invoice',
            name='amount_due',
            field=models.DecimalField(decimal_places=2, max_digits=10, null=True),
        ),
        migrations.AddField(
            model_name='invoice',
            name='date',
            field=models.DateField(auto_now_add=True, null=True),
        ),
        migrations.AddField(
            model_name='invoice',
            name='date_due',
            field=models.DateField(null=True),
        ),
        migrations.AddField(
            model_name='invoice',
            name='house',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='chatbot.houses'),
        ),
        migrations.AddField(
            model_name='invoice',
            name='is_paid',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='invoice',
            name='tenant',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='chatbot.customers'),
        ),
        migrations.AddField(
            model_name='owner',
            name='Paybill',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
        migrations.AddField(
            model_name='transactions',
            name='amount',
            field=models.DecimalField(decimal_places=2, max_digits=10, null=True),
        ),
        migrations.AddField(
            model_name='transactions',
            name='date',
            field=models.DateField(auto_now_add=True, null=True),
        ),
        migrations.AddField(
            model_name='transactions',
            name='house',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='chatbot.houses'),
        ),
        migrations.AddField(
            model_name='transactions',
            name='tenant',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='chatbot.customers'),
        ),
    ]
