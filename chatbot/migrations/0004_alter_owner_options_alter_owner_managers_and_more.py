# Generated by Django 4.2.9 on 2024-02-11 05:31

import django.contrib.auth.models
from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
        ('chatbot', '0003_owner_password_transactions'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='owner',
            options={'verbose_name': 'user', 'verbose_name_plural': 'users'},
        ),
        migrations.AlterModelManagers(
            name='owner',
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.RenameField(
            model_name='complaints',
            old_name='cus_id',
            new_name='customer_id',
        ),
        migrations.RenameField(
            model_name='complaints',
            old_name='ID',
            new_name='id',
        ),
        migrations.RenameField(
            model_name='customers',
            old_name='cus_id',
            new_name='id',
        ),
        migrations.RenameField(
            model_name='houses',
            old_name='house_rent',
            new_name='House_rent',
        ),
        migrations.RenameField(
            model_name='houses',
            old_name='house_id',
            new_name='id',
        ),
        migrations.RenameField(
            model_name='invoice',
            old_name='cusId',
            new_name='customer_id',
        ),
        migrations.RenameField(
            model_name='invoice',
            old_name='ID',
            new_name='id',
        ),
        migrations.RenameField(
            model_name='notices',
            old_name='cus_id',
            new_name='customer_id',
        ),
        migrations.RenameField(
            model_name='notices',
            old_name='ID',
            new_name='id',
        ),
        migrations.RenameField(
            model_name='owner',
            old_name='ID',
            new_name='id',
        ),
        migrations.RenameField(
            model_name='transactions',
            old_name='ID',
            new_name='id',
        ),
        migrations.RemoveField(
            model_name='owner',
            name='firstname',
        ),
        migrations.RemoveField(
            model_name='owner',
            name='lastname',
        ),
        migrations.RemoveField(
            model_name='owner',
            name='photo',
        ),
        migrations.AddField(
            model_name='owner',
            name='date_joined',
            field=models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined'),
        ),
        migrations.AddField(
            model_name='owner',
            name='first_name',
            field=models.CharField(blank=True, max_length=150, verbose_name='first name'),
        ),
        migrations.AddField(
            model_name='owner',
            name='groups',
            field=models.ManyToManyField(related_name='owners', to='auth.group'),
        ),
        migrations.AddField(
            model_name='owner',
            name='image',
            field=models.ImageField(default='profile_images/default.jpg', upload_to='profile_images/'),
        ),
        migrations.AddField(
            model_name='owner',
            name='is_active',
            field=models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active'),
        ),
        migrations.AddField(
            model_name='owner',
            name='is_staff',
            field=models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status'),
        ),
        migrations.AddField(
            model_name='owner',
            name='is_superuser',
            field=models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status'),
        ),
        migrations.AddField(
            model_name='owner',
            name='last_login',
            field=models.DateTimeField(blank=True, null=True, verbose_name='last login'),
        ),
        migrations.AddField(
            model_name='owner',
            name='last_name',
            field=models.CharField(blank=True, max_length=150, verbose_name='last name'),
        ),
        migrations.AddField(
            model_name='owner',
            name='user_permissions',
            field=models.ManyToManyField(related_name='owners', to='auth.permission'),
        ),
        migrations.AddField(
            model_name='owner',
            name='username',
            field=models.CharField(default='', max_length=150, unique=True),
        ),
        migrations.AlterField(
            model_name='houses',
            name='photo_1',
            field=models.ImageField(blank=True, upload_to='images/'),
        ),
        migrations.AlterField(
            model_name='houses',
            name='photo_2',
            field=models.ImageField(blank=True, upload_to='images/'),
        ),
        migrations.AlterField(
            model_name='houses',
            name='photo_3',
            field=models.ImageField(blank=True, upload_to='images/'),
        ),
        migrations.AlterField(
            model_name='houses',
            name='photo_4',
            field=models.ImageField(blank=True, upload_to='images/'),
        ),
        migrations.AlterField(
            model_name='owner',
            name='email',
            field=models.EmailField(blank=True, max_length=254, verbose_name='email address'),
        ),
        migrations.AlterField(
            model_name='owner',
            name='password',
            field=models.CharField(max_length=128, verbose_name='password'),
        ),
    ]