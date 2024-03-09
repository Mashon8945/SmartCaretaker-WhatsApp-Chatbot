# Generated by Django 4.2.9 on 2024-03-02 11:27

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('chatbot', '0019_alter_customers_phone'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='houses',
            name='customer',
        ),
        migrations.RemoveField(
            model_name='invoice',
            name='paybill',
        ),
        migrations.AddField(
            model_name='customers',
            name='assigned_house',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='chatbot.houses'),
        ),
        migrations.AlterField(
            model_name='houses',
            name='vacancy',
            field=models.CharField(choices=[('OCCUPIED', 'Occupied'), ('MAINTENANCE', 'Maintenance'), ('BOOKED', 'Booked'), ('VACANT', 'Vacant')], default='VACANT', max_length=20),
        ),
        migrations.CreateModel(
            name='Assignment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_assigned', models.DateField(auto_now_add=True)),
                ('house', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='chatbot.houses')),
                ('tenant', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='chatbot.customers')),
            ],
        ),
    ]