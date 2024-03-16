from decimal import Decimal
from django.http import HttpResponseBadRequest, JsonResponse,  Http404, HttpResponseRedirect
from django.shortcuts import render, HttpResponse, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.hashers import make_password
from django.contrib.auth.decorators import login_required
from twilio.rest import Client
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.lib import colors
from SmartCaretaker import settings
from .models import Owner, Houses, Customers, WhatsappMessage, Assignment, Transactions, Invoice
from .forms import AssignmentForm
from django.views.decorators.http import require_POST
from django.shortcuts import get_object_or_404
from twilio.twiml.messaging_response import MessagingResponse
from django.views.decorators.csrf import csrf_exempt
from SmartCaretaker.settings import TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN
from django.utils import timezone
from datetime import timedelta
from django.http import JsonResponse
from django.contrib import messages
from twilio.twiml.messaging_response import MessagingResponse
from django.core.paginator import Paginator
from django.utils import timezone
import uuid
import json
import requests
import os
from django.db.models import Sum
from django.urls import reverse
from django.core.exceptions import ValidationError
from django.core.files.storage import FileSystemStorage
from reportlab.pdfgen import canvas
from io import BytesIO

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

def notice(request):
    return render(request, 'notice.html')

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

    recent_trasactions = Transactions.objects.all().order_by('-id')

    active_tenants = Customers.objects.filter(is_active = 1).count()
    inactive_tenants = Customers.objects.filter(is_active = 0).count()
    total_houses = Houses.objects.all().count()
    customers = Customers.objects.all()
    vacant = Houses.objects.filter(vacancy__in = ['VACANT', 'MAINTENANCE']).count()
    
    phone_to_name = {customer.phone: (customer.firstname, customer.lastname) for customer in customers}

    messages_with_names = [
        {
            'firstname': phone_to_name[message.sender][0],
            'lastname': phone_to_name[message.sender][1],
            'content': message.body,
            'timestamp': message.timestamp
        }
        for message in recent_messages if message.sender in phone_to_name
    ]

    context = {
        'active_tenants': active_tenants, 
        'vacant': vacant,
        'messages': messages_with_names,
        'customers':customers,
        'inactive_tenants': inactive_tenants,
        'total_houses': total_houses,
    }
    return render(request, 'index.html', context)

@require_POST
@csrf_exempt
def whatsapp_webhook(request):
    if request.method == 'POST':
        sender = request.POST.get("From", "")
        receiver = request.POST.get("To", "")
        body = request.POST.get("Body", "").strip().lower()  # Convert to lowercase for case-insensitive comparison

        response = MessagingResponse()
        client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        
        # Define the text-based options
        text_options = "Menu\n1. Rent Payment\n2. Inquire Rent Arrears\n3. Request Statement\n4. Other"

        # Check if the sender is an existing tenant
        tenant = Customers.objects.filter(phone=sender).values()
        if tenant.exists():
            first_tenant = tenant[0]
            firstname = first_tenant['firstname']
            id = first_tenant['id']

            if body == 'hello':
                message = client.messages.create(
                    to=sender,
                    from_=receiver,
                    body=f"Hello {firstname},\n\nWe hope you're doing well!\nTo better assist you, please select from the following options:\n{text_options}"
                )

                print(f"Message sent! Message SID: {message.sid}")

            elif body.isdigit():
                option = int(body)
                if option == 1:
                    invoice_id = Invoice.objects.get(tenant_id=id).tenant_id
                    payment_link = generate_payment_link(request, invoice_id)
                    if payment_link:
                        response.message(f"Hello {firstname}, here is your one-time payment link: {payment_link}")
                    else:
                        response.message("Invoice not found.")

                # Inquire about rent arrears
                elif option == 2:
                    arrears_amount = Invoice.objects.filter(tenant_id=id).aggregate(Sum('arrears'))['arrears__sum'] or 0
                    response.message(f"Hello {firstname}, your current rent arrears amount is: {arrears_amount}")

                # Request statement
                elif option == 3:
                    # Logic to generate PDF
                    buffer = BytesIO()
                    doc = SimpleDocTemplate(buffer, pagesize=letter)
                    content = []

                    pdf = canvas.Canvas(buffer)

                    # Add a header
                    content.append(pdf.drawString(100, 750, "Smart Caretaker"))

                    # Create data for the table
                    data = [['Transaction ID', 'Amount', 'Date']]

                    transactions = Transactions.objects.filter(tenant_id=id)
                    
                    if transactions.exists(): 
                        pdf.drawString(100, 750, f"Hello {firstname}, here is your statement:")
                        y_position = 730  # Initial y position for drawing text

                        for transaction in transactions:
                            data.append([transaction.id, transaction.amount, transaction.date])

                        # Create a table with the data
                        table = Table(data)

                        # Add style to the table
                        style = TableStyle([
                            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                            ('GRID', (0, 0), (-1, -1), 1, colors.black)
                        ])
                        table.setStyle(style)

                        # Add the table to the content
                        content.append(table)

                        # Build the PDF
                        doc.build(content)
                        buffer.seek(0)


                        # Save PDF to a file
                        try:
                            fs = FileSystemStorage(location=r'C:\Users\Leona\Desktop\Smart Caretaker\Chatbot\static\statements')
                            filename = 'statement.pdf'
                            pdf_path = fs.save(filename, buffer)

                            pdf_url = fs.url(pdf_path)
                            print(f"PDF saved at: {pdf_url}")

                            # Send the PDF as a media message
                            try:
                                message = client.messages.create(
                                    to=sender,
                                    from_=receiver,
                                    media_url=[request.build_absolute_uri(pdf_url)]
                                )

                                print(f"Media message sent! Message SID: {message.sid}")
                            except Exception as e:
                                print(f"Error sending media message: {e}")
                                response.message("Error sending media message. Please try again later.")
                        except Exception as e:
                            print(f"Error saving PDF: {e}")
                            response.message("Please try again later.")

                elif option == 4:
                    # Prompt the user to specify their inquiry
                    response.message(f"Hello {firstname}, please type and specify your inquiry.")

                    next_message_body = listen_for_next_message(sender)  # This function should capture the next message from the user

                    if next_message_body:
                        WhatsappMessage.objects.create(sender=sender, body=next_message_body, receiver=receiver)
                        response.message(f"Thank you {firstname}, we have received your message. Our team will get back to you shortly.")
                    else:
                        response.message("No message received. Please try again later.")
                else:
                    response.message(f"Hello {firstname}, please select a valid option or send 'menu' to see options again.")

            # Provide main menu
            elif body == 'menu':
                response.message(f"Hello {firstname},\n\nPlease select from the following options:\n{text_options}")
            else:
                response.message("We couldn't find your information in our records. Please contact support for assistance.")

            return HttpResponse(str(response), content_type='application/xml', status=200)
        else:
            return HttpResponse("Invalid request", content_type='application/xml', status=400)


def listen_for_next_message(sender):
    # Initialize Twilio client
    client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)

    # Fetch recent messages from Twilio
    messages = client.messages.list(to=sender, limit=1)  # Limit to 1 message for simplicity

    # Check if there are any incoming messages
    if messages:
        message_body = messages[0].body  # Get the body of the first message
        return message_body
    else:
        return None



@login_required(login_url='/login/')
def homes(request):
    tenants = Customers.objects.all()
    form = AssignmentForm() 
    assignments = Assignment.objects.select_related('house', 'tenant')

    house_paginate = Paginator(Houses.objects.all(), 10)
    page = request.GET.get('page')
    page_house = house_paginate.get_page(page)

    page_number = request.GET.get('page', 1)  # Get the current page number
    items_per_page = 10  # Assuming 10 items per page, adjust as per your pagination setup
    index_offset = (int(page_number) - 1) * items_per_page

    if request.method == 'POST':
        form = AssignmentForm(request.POST)
        if form.is_valid():
            house_id = form.cleaned_data['house'].id
            customer_id = form.cleaned_data['tenant'].id

            assignment = form.save(commit=False)

            houses = Houses.objects.get(id=house_id)
            customer = Customers.objects.get(id=customer_id)
            cust_num = customer.id

            assignment = Assignment(tenant=customer, house=houses)

            if assignment.house.is_vacant():
                assignment.save()
                tenant = Customers.objects.get(pk=cust_num)
                tenant.assigned_house = houses
                tenant.is_active = 1
                tenant.save()
                return JsonResponse({'status': 'success', 'message': 'House has been successfully assigned to the tenant.'})
            else:
                return JsonResponse({'status': 'success', 'message':'This house is not vacant'}, status=500)
        else:
            return JsonResponse({'status': 'error', 'message': form.errors}, status=400)

    context = {
        'tenants': tenants,
        'form': form,  
        'assignments': assignments,
        'page_house': page_house,
        'index_offset': index_offset,
    }
    return render(request, 'homes.html', context)

@login_required(login_url='/login/')
def unassign_house(request, assignment_id):
    if request.method == 'POST':
        assignment = get_object_or_404(Assignment, id=assignment_id)
        house = assignment.house
        tenant = assignment.tenant

        house.make_vacant()
        
        tenant.assigned_house = None
        tenant.is_active = 0
        tenant.save()
        
        assignment.delete()
        
        messages.success(request, 'Tenant has been successfully unassigned from the house')
        return redirect('homes')
    else:
        messages.error(request, 'An error has occured while unassigning tenant')
        return redirect('homes')

@login_required(login_url='/login/')
def add_homes(request):
    if request.method == 'POST':
        house_type = request.POST.get('houseType')
        address = request.POST.get('address')
        city = request.POST.get('city')
        House_rent = request.POST.get('rent')
        vacancy = request.POST.get('status')

        if not house_type or not address or not House_rent or not city or not vacancy:
            return HttpResponseBadRequest('Missing Field!')
        try:
            Houses.objects.create(
                house_type = house_type,
                address = address,
                city = city,
                House_rent = House_rent,
                vacancy = vacancy
            )
            return JsonResponse({'status': 'success', 'message': 'Tenant added successfully!'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': 'An error occurred while adding new Tenant.'}, status=500)
    else:
        return HttpResponseBadRequest('Invalid request')
    
@login_required(login_url='/login/')
def delete_house(request, house_id):
    house = get_object_or_404(Houses, id=house_id)
    house.delete()

    messages.success(request, 'House deleted successfully!')
    return redirect('homes')


@require_POST
@login_required(login_url='/login/')
def update_homes(request):
    if request.method == 'POST':
        house_id = request.POST.get('id')
        house_type = request.POST.get('houseType')
        address = request.POST.get('address')
        city = request.POST.get('city')
        rent = request.POST.get('rent')
        status = request.POST.get('status')

        if not all([house_id, house_type, address, city, rent, status]):
            return HttpResponseBadRequest('Missing Fields')

        try:
            house = Houses.objects.get(pk=house_id)
            house.house_type = house_type
            house.address = address
            house.city = city
            house.House_rent = rent
            house.vacancy = status
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
        'status': house.vacancy
    }     
    return JsonResponse(data)
    

@login_required(login_url='/login/')
def tenants(request):
    customer_paginate = Paginator(Customers.objects.all().order_by('-is_active'), 10)
    cus_page = request.GET.get('page')
    customer = customer_paginate.get_page(cus_page)

    page_number = request.GET.get('page', 1) 
    items_per_page = 10 
    index_offset = (int(page_number) - 1) * items_per_page

    houses = Houses.objects.all()
    context = {
        'cus': customer,
        'houses': houses,
        'index_offset' : index_offset,
    }
    return render(request, 'customers.html', context)

@login_required(login_url='/login/')
def add_customer(request):
    if request.method == 'POST':
        firstname = request.POST.get('firstname')
        lastname = request.POST.get('lastname')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        active = request.POST.get('active')

        if not firstname or not lastname or not email or not phone:
            return HttpResponseBadRequest('Missing Field!')
        try:
            Customers.objects.create(
                firstname = firstname,
                lastname = lastname,
                email = email,
                phone = 'whatsapp:' +phone,
                is_active = active
            )
            return JsonResponse({'status': 'success', 'message': 'Tenant added successfully!'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': 'An error occurred while adding new Tenant.'}, status=500)
    else:
        return HttpResponseBadRequest('Invalid request')


@require_POST
@login_required(login_url='/login/')
def update_Customer(request):
    if request.method == 'POST':
        customer_id = request.POST.get('id')
        firstname = request.POST.get('firstname')
        lastname = request.POST.get('lastname')
        email = request.POST.get('email')
        phone = request.POST.get('phone')

        if not all([customer_id, firstname, lastname, email, phone ]):
            return HttpResponseBadRequest('Missing Fields')

        try:
            customer = Customers.objects.get(pk=customer_id)
            customer.firstname = firstname
            customer.lastname = lastname
            customer.phone = phone
            customer.email = email
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

@login_required(login_url='/login/')
def delete_customer(request, customer_id):
    customer = get_object_or_404(Customers, id=customer_id)
    customer.delete()

    messages.success(request, "Tenant deleted successfully ")
    return redirect('tenants')  

@login_required(login_url='/login/')
def transactions(request):
    transactions = Paginator(Transactions.objects.all().order_by('-date'), 10)
    transaction_page = request.GET.get('page')
    transaction = transactions.get_page(transaction_page)

    page_number = request.GET.get('page', 1) 
    items_per_page = 10 
    index_offset = (int(page_number) - 1) * items_per_page

    return render(request, 'transactions.html', {'transaction':transaction, 'index_offset': index_offset})


def generate_payment_link(request, invoice_id):
    try:
        invoice = Invoice.objects.get(id=invoice_id)
        # Generate a unique identifier for the payment
        payment_uuid = uuid.uuid4()
        invoice.payment_uuid = payment_uuid 
        invoice.save()

        payment_link = request.build_absolute_uri(reverse('payment_form', kwargs={'payment_uuid': payment_uuid}))
        print(payment_link)
        messages.success(request, 'Link has been sent successfully')
        return payment_link
    except Invoice.DoesNotExist:
        messages.error(request, 'Invoice does not exist')
    return redirect('invoice_list')

@login_required(login_url='/login/')
def send_invoices(request):
    occupied_houses = Houses.objects.exclude(vacancy='VACANT')
    current_date = timezone.now().date()
    
    for house in occupied_houses:
        try:
            customer = Customers.objects.get(assigned_house=house, is_active=True)
        except Customers.DoesNotExist:
            # If no active customer is assigned, skip this house
            continue

        # Check if an invoice already exists for the current period and is not paid
        existing_invoice = Invoice.objects.filter(
            tenant=customer,
            date__month=current_date.month,
            date__year=current_date.year
        ).exists()

        if not existing_invoice:
            rent_choices = dict(Houses.HouseRent.choices)
            rent_amount_str = house.House_rent

            if rent_amount_str in rent_choices:
                rent_amount = Decimal(rent_choices[rent_amount_str])

                new_invoice = Invoice(
                    tenant=customer,
                    house=house,
                    date_due=current_date + timezone.timedelta(days=30),  # Due in 30 days from now
                    amount_due=rent_amount,
                    total_due=rent_amount,  # Assuming no arrears, fines, or maintenance fees for simplicity
                    payment_uuid=uuid.uuid4()  # Unique payment identifier
                )
                new_invoice.save()
                messages.success(request, f'Invoice generated for house H({house.id}) and send to tenant')
            else:
                messages.error(request, f'Invalid rent amount for house H({house.id})')

    return redirect('invoice_list')

@login_required(login_url='/login/')
def view_invoice(request, invoice_id):
    invoice = Invoice.objects.get(id=invoice_id)
    return render(request, 'invoice.html', {'invoice': invoice})

@login_required(login_url='/login/')
def invoice_list(request):
    invoice = Paginator(Invoice.objects.all().order_by('-date'), 10)
    invoice_page = request.GET.get('page')
    invoices = invoice.get_page(invoice_page)

    page_number = request.GET.get('page', 1) 
    items_per_page = 10 
    index_offset = (int(page_number) - 1) * items_per_page

    return render(request, 'invoice_list.html', {'invoices': invoices, 'index_offset': index_offset})


def payment_form(request, payment_uuid):
    context = {'errors': []}

    invoice = get_object_or_404(Invoice, payment_uuid=payment_uuid)

    if request.method == 'POST':
        try:
            amount_paid = Decimal(request.POST.get('amount_paid', '0.00'))  # Convert input to Decimal
            if amount_paid <= 0:
                raise ValidationError("Invalid payment amount.")

            if amount_paid > invoice.total_due:
                raise ValidationError("Payment exceeds the amount due.")

            if invoice.is_paid:
                raise ValidationError("Payment already processed.")

            transaction = Transactions(
                house=invoice.house,
                tenant=invoice.tenant,
                invoice=invoice,
                amount=amount_paid
            )
            transaction.save()

            invoice.amount_due -= amount_paid
            invoice.arrears = max(invoice.arrears - amount_paid, 0) 
            if invoice.amount_due <= 0:
                invoice.is_paid = True  # Mark as paid if the total due is zero or less
            invoice.save()

            return HttpResponseRedirect(reverse('payment_success', kwargs={'transaction_id': transaction.id}))

        except ValidationError as e:
            # Add validation error messages to the context.
            context['errors'].extend(e.messages)
        except Exception as e:
            # Add any other exception messages to the context.
            context['errors'].append(str(e))

    context.update({
        'tenant_name': invoice.tenant.firstname + ' ' + invoice.tenant.lastname,
        'house_details': invoice.house.id,
        'rental_arrears': invoice.arrears,
        'invoice_id': invoice.id,
        'amount_due': invoice.total_due,
    })

    return render(request, 'payments.html', context)

def payment_success(request, transaction_id):
    transaction = Transactions.objects.get(id=transaction_id)
    context = {
        'transaction': transaction,
        'message': "Thank you for your payment!",
    }
    return render(request, 'success.html', context)