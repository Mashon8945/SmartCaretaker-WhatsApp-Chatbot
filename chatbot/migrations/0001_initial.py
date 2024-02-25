# Generated by Django 4.2.9 on 2024-02-07 07:21

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Customers',
            fields=[
                ('cus_id', models.AutoField(primary_key=True, serialize=False)),
                ('firstname', models.CharField(max_length=255)),
                ('lastname', models.CharField(max_length=255)),
                ('phone', models.CharField(max_length=15)),
                ('email', models.EmailField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='Houses',
            fields=[
                ('house_id', models.AutoField(primary_key=True, serialize=False)),
                ('house_type', models.CharField(choices=[('Bedsitter', 'Bedsitter'), ('1 Bedroom', 'Onebedroom'), ('2 Bedroom', 'Twobedroom'), ('3 Bedroom', 'Threebedroom')], default='Bedsitter', max_length=20)),
                ('address', models.CharField(max_length=255)),
                ('city', models.CharField(max_length=255)),
                ('house_rent', models.CharField(choices=[('15000', 'Bedsitter'), ('25000', 'Onebedroom'), ('35000', 'Twobedroom'), ('50000', 'Threebedroom')], default='15000', max_length=20)),
                ('vacancy', models.CharField(choices=[('Occuppied', 'Occuppied'), ('Booked', 'Booked'), ('Vacant', 'Vacant')], default='Vacant', max_length=20)),
                ('photo_1', models.ImageField(upload_to='static/images')),
                ('photo_2', models.ImageField(upload_to='static/images')),
                ('photo_3', models.ImageField(upload_to='static/images')),
                ('photo_4', models.ImageField(upload_to='static/images')),
            ],
        ),
        migrations.CreateModel(
            name='Notices',
            fields=[
                ('ID', models.AutoField(primary_key=True, serialize=False)),
                ('notice', models.TextField()),
                ('cus_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='chatbot.customers')),
                ('house_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='chatbot.houses')),
            ],
        ),
        migrations.CreateModel(
            name='Invoice',
            fields=[
                ('ID', models.AutoField(primary_key=True, serialize=False)),
                ('paybill', models.CharField(max_length=255)),
                ('total', models.IntegerField()),
                ('cusId', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='chatbot.customers')),
                ('house_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='chatbot.houses')),
            ],
        ),
        migrations.AddField(
            model_name='customers',
            name='house',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='chatbot.houses'),
        ),
        migrations.CreateModel(
            name='Complaints',
            fields=[
                ('ID', models.AutoField(primary_key=True, serialize=False)),
                ('cus_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='chatbot.customers')),
                ('house_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='chatbot.houses')),
            ],
        ),
    ]
