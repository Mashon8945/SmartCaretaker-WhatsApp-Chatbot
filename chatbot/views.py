from django.http import HttpResponseBadRequest, JsonResponse
from django.shortcuts import render, HttpResponse, redirect, HttpResponseRedirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.hashers import make_password
from django.contrib.auth.decorators import login_required
from twilio.rest import Client
from .models import Owner, Houses, Customers, WhatsappMessage
from django.views.decorators.http import require_POST
from django.shortcuts import get_object_or_404
from twilio.twiml.messaging_response import MessagingResponse
from django_twilio.decorators import twilio_view
from django.views.decorators.csrf import csrf_exempt
from SmartCaretaker.settings import TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN
from django.utils import timezone
from datetime import timedelta
from django.http import JsonResponse
from django.db.models import Q
from django.contrib.auth.models import User

# Create your views here.
def landing(request):
    return render(request, 'landingpage.html')

def register_owner(request):
    context = {'errors': []}
    if request.method == 'POST':
        firstname = request.POST.get('firstname')
        lastname = request.POST.get('lastname')
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        image = request.FILES.get('image')

        if password1 != password2:
            context['errors'].append("Passwords do not match")
        if Owner.objects.filter(email=email).exists():
            context['errors'].append("Email is already in use!")
        
        if not context['errors']:
            owner = Owner(
                first_name = firstname, 
                last_name = lastname, 
                email = email,
                is_active = 1,
                is_staff = 1,
                username = email,
                is_superuser = 0,
                password = make_password(password1),
                image = image
            )
            owner.save()
            login(request, owner)
            return redirect('login_owner')

    return render(request, 'signup.html', context)

def login_owner(request):
    context = {'errors':[]}
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = authenticate(request, username=email, password=password)

        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            context['errors'].append("Incorrect email or password!")

    return render(request, 'login.html', context)

@login_required(login_url='/login/')
def header(request):
    owner = request.user
    context = {
        'owner': owner,
    }
    return render(request, 'header.html', context)

@login_required(login_url='/login/')
def dashboard(request):
    if request.method == 'POST':
        message_id = request.POST.get('message_id')
        reply = request.POST.get('reply')

        message_to_reply = WhatsappMessage.objects.get(id = message_id)
        client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        from_whatsapp_number = 'whatsapp:+14155238886'
        to_whatsapp_number = message_to_reply.sender

        client.messages.create(body = reply, from_ = from_whatsapp_number, to = to_whatsapp_number)
        message_to_reply.replied = True
        message_to_reply.save()

        return redirect('dashboard')

    current_time = timezone.now()
    two_days_ago = current_time - timedelta(days=2)
    recent_messages = WhatsappMessage.objects.filter(timestamp__gte=two_days_ago).order_by('-timestamp')

    tenants = Customers.objects.filter(is_active = 1).count()
    customers = Customers.objects.all()
    vacant = Houses.objects.filter(vacancy__in = ['Vacant', 'Maintenance']).count()

    print(recent_messages)
    
    phone_to_name = {customer.phone: customer.firstname for customer in customers}

    messages_with_names = [
        {
            'name': phone_to_name.get(message.sender, 'Uknown'),
            'content': message.body,
            'timestamp': message.timestamp
        }
        for message in recent_messages if message.sender in phone_to_name
    ]

    context = {
        'tenants': tenants, 
        'vacant': vacant,
        'messages': messages_with_names,
        'customers':customers,
    }
    return render(request, 'index.html', context)

@csrf_exempt
def whatsapp(request):
    if request.method == 'POST':
        sender = request.POST.get("From", "")
        receiver = request.POST.get("To", "")
        body = request.POST.get("Body", "")

        WhatsappMessage.objects.create(sender = sender, receiver = receiver,body = body)
        return HttpResponse("Thank you for your message. We have received it and will get back to you", status=200)
    else:
        return HttpResponse("Invalid request", status = 200)
    
@login_required(login_url='/login/')
def homes(request):
    houses = Houses.objects.all()
    tenants = Customers.objects.all()
    context = {
        'houses': houses,
        'tenants': tenants,
    }
    return render(request, 'homes.html', context)

@login_required(login_url='/login/')
def add_homes(request):
    if request.method == 'POST':
        house_type = request.POST.get('houseType')
        address = request.POST.get('address')
        city = request.POST.get('city')
        House_rent = request.POST.get('rent')
        tenants = request.POST.get('tenants')
        vacancy = request.POST.get('status')

        if not house_type or not address or not House_rent or not city or not vacancy:
            return HttpResponseBadRequest('Missing Field!')
        try:
            Houses.objects.create(
                house_type = house_type,
                address = address,
                city = city,
                House_rent = House_rent,
                vacancy = vacancy,
                customer_id = tenants
            )
            return JsonResponse({'status': 'success', 'message': 'Tenant added successfully!'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': 'An error occurred while adding new Tenant.'}, status=500)
    else:
        return HttpResponseBadRequest('Invalid request')


@require_POST
def update_homes(request):
    if request.method == 'POST':
        house_id = request.POST.get('id')
        house_type = request.POST.get('houseType')
        address = request.POST.get('address')
        city = request.POST.get('city')
        rent = request.POST.get('rent')
        status = request.POST.get('status')
        tenant = request.POST.get('tenant')

        if not all([house_id, house_type, address, city, rent, status]):
            return HttpResponseBadRequest('Missing Fields')

        try:
            house = Houses.objects.get(pk=house_id)
            house.house_type = house_type
            house.address = address
            house.city = city
            house.House_rent = rent
            house.vacancy = status
            house.customer_id = tenant
            house.save()

            return JsonResponse({'status': 'success', 'message': 'House updated successfully!'})
        except Houses.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'House does not exist!'}, status=404)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': 'An error occurred while updating house.'}, status=500)

    else:
        return HttpResponseBadRequest('Invalid request!')
    
@login_required(login_url='/login/')
def get_house_details(request, house_id):
    house = get_object_or_404(Houses, pk=house_id)

    data = {
        'id':house.id,
        'address': house.address,
        'city': house.city,
        'rent': house.House_rent,
        'house_type': house.house_type,
        'status': house.vacancy,
        'tenant': house.customer_id,
    }     
    return JsonResponse(data)
    

@login_required(login_url='/login/')
def tenants(request):
    customer = Customers.objects.all()
    houses = Houses.objects.all()
    context = {
        'cus': customer,
        'houses': houses,
    }
    return render(request, 'customers.html', context)

@login_required(login_url='/login/')
def add_customer(request):
    if request.method == 'POST':
        firstname = request.POST.get('firstname')
        lastname = request.POST.get('lastname')
        email = request.POST.get('email')
        phone = request.POST.get('phone')

        if not firstname or not lastname or not email or not phone:
            return HttpResponseBadRequest('Missing Field!')
        try:
            Customers.objects.create(
                firstname = firstname,
                lastname = lastname,
                email = email,
                phone = phone
            )
            return JsonResponse({'status': 'success', 'message': 'Tenant added successfully!'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': 'An error occurred while adding new Tenant.'}, status=500)
    else:
        return HttpResponseBadRequest('Invalid request')


@require_POST
def update_Customer(request):
    if request.method == 'POST':
        customer_id = request.POST.get('id')
        firstname = request.POST.get('firstname')
        lastname = request.POST.get('lastname')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        active = request.POST.get('active')

        if not all([customer_id, firstname, lastname, email, phone]):
            return HttpResponseBadRequest('Missing Fields')

        try:
            customer = Customers.objects.get(pk=customer_id)
            customer.firstname = firstname
            customer.lastname = lastname
            customer.phone = phone
            customer.email = email
            customer.is_active = active
            customer.save()

            return JsonResponse({'status': 'success', 'message': 'Customer updated successfully!'})
        except Customers.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Customer does not exist!'}, status=404)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': 'An error occurred while updating the customer.'}, status=500)

    else:
        return HttpResponseBadRequest('Invalid request!')
    
@login_required(login_url='/login/')
def get_tenant_details(request, customer_id):
    customer = get_object_or_404(Customers, pk=customer_id)

    data = {
        'id':customer.id,
        'firstname': customer.firstname,
        'lastname': customer.lastname,
        'email': customer.email,
        'phone': customer.phone,
        'active': customer.is_active,
    }    
    return JsonResponse(data)