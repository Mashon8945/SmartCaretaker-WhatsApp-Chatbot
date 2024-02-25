from django.db import models
from django.utils import timezone
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import Group, Permission


class Owner(AbstractUser):
    id = models.AutoField(primary_key=True)
    username = models.CharField(max_length=150, unique=True, default='')
    image = models.ImageField(upload_to='profile_images/', default='profile_images/default.jpg')
    groups = models.ManyToManyField(Group, related_name='owners')
    user_permissions = models.ManyToManyField(Permission, related_name='owners')
    
    def __str__(self):
        return self.email

class Customers(models.Model):
    id = models.AutoField(primary_key=True)
    firstname = models.CharField(max_length = 255)
    lastname = models.CharField(max_length = 255)
    phone = models.CharField(max_length = 15)
    email = models.EmailField(max_length = 255)
    is_active = models.BooleanField()

    def __str__(self):
        return self.firstname
    
class Houses(models.Model):
    class vacant(models.TextChoices):
        OCCUPPIED = 'Occuppied'
        BOOKED = 'Booked'
        VACANT = 'Vacant'
        MAINTENANCE = 'Maintenance'
    class HouseType(models.TextChoices):
        BEDSITTER = 'Bedsitter'
        ONE_BEDROOM = '1 Bedroom'
        TWO_BEDROOM = '2 Bedroom'
        THREE_BEDROOM = '3 Bedroom'
    class HouseRent(models.TextChoices):
        BEDSITTER = ('15000', '15000')
        ONE_BEDROOM = ('25000', '25000')
        TWO_BEDROOM = ('35000', '35000')
        THREE_BEDROOM = ('50000', '50000')

    id = models.AutoField(primary_key=True)
    house_type = models.CharField(max_length=20, choices=HouseType.choices, default=HouseType.BEDSITTER)
    address = models.CharField(max_length=255)
    city = models.CharField(max_length = 255)
    House_rent = models.CharField(max_length = 20, choices = HouseRent.choices, default = HouseRent.BEDSITTER)
    vacancy  = models.CharField(max_length = 20, choices = vacant.choices, default = vacant.VACANT)
    customer = models.ForeignKey(Customers, on_delete = models.CASCADE, null = True)

    def __str__(self):
        return self.address


class Invoice(models.Model):
    id = models.AutoField(primary_key=True)
    customer_id = models.ForeignKey(Customers, on_delete = models.CASCADE)
    house_id = models.ForeignKey(Houses, on_delete = models.CASCADE)
    paybill = models.CharField(max_length = 255)
    total = models.IntegerField()

    def __str__(self):
        return self.paybill

class Transactions(models.Model):
    id = models.AutoField(primary_key=True)
    house_id = models.ForeignKey(Houses, on_delete = models.CASCADE)
    month = models.DateField()

    def save(self, *args, **kwargs):
        # If month is not already set, set it to the current month and year
        if not self.month:
            self.month = timezone.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        super(Transactions, self).save(*args, **kwargs)
    def __str__(self):
        return self.house_id

class Notices(models.Model):
    id = models.AutoField(primary_key=True)
    customer_id = models.ForeignKey(Customers, on_delete = models.CASCADE)
    house_id = models.ForeignKey(Houses, on_delete = models.CASCADE)
    notice = models.TextField()

    def __str__(self):
        return self.notice

class Complaints(models.Model):
    id = models.AutoField(primary_key=True)
    customer_id = models.ForeignKey(Customers, on_delete = models.CASCADE)
    house_id = models.ForeignKey(Houses, on_delete = models.CASCADE)
    complaint = models.TextField(null=True)

    def __str__(self):
        return self.complaint
    
class WhatsappMessage(models.Model):
    sender = models.CharField(max_length = 255)
    receiver = models.CharField(max_length = 255)
    body = models.URLField(blank = True, null = True)
    timestamp = models.DateTimeField(auto_now_add = True)

    def __str__(self):
        return f"{self.sender} > {self.receiver}: {self.body}"
