from django.db import models
from django.utils import timezone
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import Group, Permission
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
import uuid

class Owner(AbstractUser):
    id = models.AutoField(primary_key=True)
    username = models.CharField(max_length=150, unique=True, default='')
    image = models.ImageField(upload_to='profile_images/', default='profile_images/default.jpg')
    groups = models.ManyToManyField(Group, related_name='owners')
    user_permissions = models.ManyToManyField(Permission, related_name='owners')
    Paybill = models.CharField(max_length = 20, blank=True, null=True)
    
    def __str__(self):
        return self.email

class Houses(models.Model):
    STATUS_CHOICES = [
        ('OCCUPIED', 'Occupied'),
        ('MAINTENANCE', 'Maintenance'),
        ('BOOKED', 'Booked'),
        ('VACANT', 'Vacant'),
    ]
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
    vacancy  = models.CharField(max_length = 20, choices = STATUS_CHOICES, default = 'VACANT')

    def __str__(self):
        return f"{self.id} {self.house_type}"
    
    def is_vacant(self):
        return self.vacancy == 'VACANT'
    
    def make_vacant(self):
        self.vacancy = 'VACANT'
        self.save()

class Customers(models.Model):
    id = models.AutoField(primary_key=True)
    firstname = models.CharField(max_length = 255)
    lastname = models.CharField(max_length = 255)
    phone = models.CharField(max_length = 255)
    email = models.EmailField(max_length = 255)
    is_active = models.BooleanField()
    assigned_house = models.ForeignKey(Houses, on_delete=models.SET_NULL, null=True, blank=True)
    awaiting_response = models.BooleanField(null=False, default=False)

    def __str__(self):
        return  f"{self.id} {self.firstname} {self.lastname} {self.assigned_house}"
    
class CustomerState(models.Model):
    phone = models.CharField(max_length=30, unique=True)
    state = models.CharField(max_length=50)
    selected_house_id = models.IntegerField(null=True, blank=True)

class Assignment(models.Model):
    tenant = models.ForeignKey(Customers, on_delete=models.CASCADE)
    house = models.ForeignKey(Houses, on_delete=models.SET_NULL, null=True, blank=True)
    date_assigned = models.DateField(auto_now_add=True)

    def clean(self):
        if self.house.vacancy != 'VACANT':
            raise ValidationError(_('The house is not vacant.'))

    def save(self, *args, **kwargs):
        if not self.pk: 
            self.house.vacancy = 'OCCUPIED'
            self.house.save()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.tenant.firstname, self.tenant.lastname} assigned to {self.house.house_type}"

class Invoice(models.Model):
    id = models.AutoField(primary_key=True)
    tenant = models.ForeignKey(Customers, on_delete = models.CASCADE, null=True)
    house = models.ForeignKey(Houses, on_delete = models.CASCADE, null=True)
    date = models.DateField(auto_now_add=True, null=True)
    amount_due = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    date_due = models.DateField(null=True)
    is_paid = models.BooleanField(default=False)
    arrears = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    fines = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    maintenance_fees = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_due = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    payment_uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, null=True)

    def __str__(self):
        return self.amount_due
    
    def save(self, *args, **kwargs):
        self.total_due = self.amount_due + self.arrears + self.fines + self.maintenance_fees
        super(Invoice, self).save(*args, **kwargs)

class Transactions(models.Model):
    id = models.AutoField(primary_key=True)
    house = models.ForeignKey(Houses, on_delete = models.SET_NULL, null=True)
    tenant = models.ForeignKey(Customers, on_delete=models.SET_NULL, null=True)
    invoice = models.ForeignKey(Invoice, related_name='transactions', on_delete=models.SET_NULL, null=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    date = models.DateField(auto_now_add=True, null=True)

    def __str__(self):
        return self.id

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
    body = models.TextField(blank = True, null = True, max_length = 10000)
    timestamp = models.DateTimeField(auto_now_add = True)
    replied = models.BooleanField(null=False, default=False)

    def __str__(self):
        return f"{self.sender} > {self.receiver}: {self.body}"

class AdminMessage(models.Model):
    tenant = models.ForeignKey(Customers, on_delete=models.CASCADE)  # Reference to the user
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['timestamp']