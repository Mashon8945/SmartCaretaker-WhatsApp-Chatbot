from decimal import Decimal
from django.http import HttpResponseBadRequest, JsonResponse, HttpResponseRedirect
from django.shortcuts import render, HttpResponse, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.hashers import make_password
from django.contrib.auth.decorators import login_required
from twilio.rest import Client
from .models import Owner, Houses, Customers, WhatsappMessage, Assignment, Transactions, Invoice, CustomerState
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
from django.db.models import Sum
from django.urls import reverse
from django.core.exceptions import ValidationError


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
    messages = WhatsappMessage.objects.all().order_by('-timestamp')
    customers = Customers.objects.all()

    phone_to_name = {customer.phone: (customer.firstname, customer.lastname) for customer in customers}
    messages_with_names = [
        {
            'firstname': phone_to_name[message.sender][0],
            'lastname': phone_to_name[message.sender][1],
            'content': message.body,
            'timestamp': message.timestamp
        }
        for message in messages if message.sender in phone_to_name
    ]
    context = {
        'messages': messages_with_names,
        'customers':customers,
    }
    return render(request, 'notice.html', context)

@login_required(login_url='/login/')
@csrf_exempt
def dashboard(request):
    if request.is_ajax():
        message_id = request.POST.get('message_id')
        reply_text = request.POST.get('reply_text')

        message_to_reply = WhatsappMessage.objects.get(id = message_id)
        client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        from_whatsapp_number = 'whatsapp:+14155238886'
        to_whatsapp_number = message_to_reply.sender

        client.messages.create(body = reply_text, from_ = from_whatsapp_number, to = to_whatsapp_number)
        message_to_reply.replied = True
        message_to_reply.save()

        # After saving the reply or sending the message, return a JsonResponse
        return JsonResponse({'reply_text': reply_text}, status=200)
        

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
            'id': message.id,
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
        body = request.POST.get("Body", "").strip().title()

        response = MessagingResponse()
        client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        
        # Define the text-based options
        text_options = "Menu\n1. Rent Payment\n2. Inquire Rent Arrears\n3. Request Statement\n4. Other(specify)"

        # Check if the sender is an existing tenant
        tenant = Customers.objects.filter(phone=sender).first()
        if tenant:
            firstname = tenant.firstname
            id = tenant.id

            if tenant.awaiting_response:
                # Capture the message and save to the database
                WhatsappMessage.objects.create(sender=sender, body=body, receiver=receiver)

                # Reset the flag in the database
                tenant.awaiting_response = False
                tenant.save()

                # Send confirmation to the user
                response.message(f"Thank you {firstname}, we have received your message. Our team will get back to you shortly.")
            else:
                if body in ['Hello', 'Hi', 'Hey', 'Sasa', 'Mambo']:
                    message = client.messages.create(
                        to=sender,
                        from_=receiver,
                        body=f"Hello {firstname},\n\nWe hope you're doing well!\nTo better assist you, please select from the following options:\n{text_options}"
                    )
                    print(f"Message sent! Message SID: {message.sid}")
                elif body.isdigit():
                    option = int(body)
                    if option == 1:
                        invoice_id = Invoice.objects.filter(tenant_id=id).first().id
                        payment_link = generate_payment_link(request, invoice_id)
                        if payment_link:
                            response.message(f"Hello {firstname}, here is your one-time payment link: {payment_link}")
                        else:
                            response.message("Invoice not found.")

                    # Inquire about rent arrears
                    elif option == 2:
                        arrears_amount = Invoice.objects.filter(tenant_id=id).aggregate(Sum('amount_due'))['amount_due__sum'] or 0
                        response.message(f"Hello {firstname}, your current rent arrears amount is: Ksh {arrears_amount}")

                    # Request statement
                    elif option == 3:
                        # Fetch transactions for the tenant
                        transactions = Transactions.objects.filter(tenant_id=id)
                        
                        if transactions.exists():
                            # Initialize a message string with a header
                            message_body = f"Hello {firstname}, here is your statement:\n\n"
                            message_body += "No. \tTx ID \tAmount  \tDate \n\n"  # Column headers

                            # Iterate through transactions and append each to the message string
                            for counter, transaction in enumerate(transactions, start=1):
                                message_body += f"{counter}. \t{transaction.id} \t{transaction.amount} \t{transaction.date.strftime('%Y-%m-%d')}\n"

                            # Send the message with the transactions formatted as text
                            try:
                                message = client.messages.create(
                                    to=sender,
                                    from_=receiver,
                                    body=message_body
                                )
                                print(f"Message sent! Message SID: {message.sid}")
                            except Exception as e:
                                print(f"Error sending message: {e}")
                                response.message("Error sending message. Please try again later.")
                        else:
                            response.message("No transactions found.")
                    elif option == 4:
                        # Set a flag in the database to indicate that the next message should be captured
                        tenant.awaiting_response = True
                        tenant.save()

                        # Prompt the user to specify their inquiry
                        response.message(f"Hello {firstname}, please type and specify your inquiry.")
                    else:
                        response.message(f"Hello {firstname}, please select a valid option or send 'menu' to see options again.")
                else:
                    response.message(f"Hello {firstname},\n\nPlease select from the following options:\n{text_options}")
        else:
            # Get or create a state object for the user
            state, created = CustomerState.objects.get_or_create(phone=sender)
            
            if state.state == '':
                if body.lower() == 'quit':
                    response.message("You have ended the conversation. Have a great day! ")
                    state.delete()
                else:
                    # If the state is empty, this is the first interaction
                    response.message("We couldn't find your information in our records. " 
                                    "Are you looking for a house? \n\nPlease reply with 'Yes' to view available houses or 'No' to end this conversation.")
                    state.state = 'awaiting_house_interest'
                    state.save()

            elif state.state == 'awaiting_house_interest':
                if body.lower() == 'quit':
                    response.message("You have ended the conversation. Have a great day!")
                    state.delete()
                elif body == 'Yes':
                    # The user is interested in a house, show available houses
                    vacant_houses = Houses.objects.filter(vacancy='VACANT')
                    if vacant_houses.exists():
                        house_list = "Please select a house by number:\n\n No.\t Name\t Type\t\t Rent\n"
                        for index, house in enumerate(vacant_houses, start=1):
                            house_list += f"{index}. \tH({house.id}) \t{house.house_type} \tKsh {house.House_rent}\n"
                        response.message(house_list)
                        state.state = 'awaiting_house_selection'
                        state.save()
                    else:
                        response.message("Currently, there are no vacant houses available.")
                        state.state = ''
                        state.save()
                elif body == 'No':
                    response.message("Thank you for your response. Have a great day!")
                    state.delete()  # Clean up the state if the user is not interested
                else:
                    response.message("I didn't understand that. Are you looking for a house? Please reply with 'Yes' or 'No' or 'Quit'.")

            elif state.state == 'awaiting_house_selection':
                if body.lower() == 'quit':
                    response.message("You have ended the conversation. Have a great day!")
                    state.delete()
                else:
                    try:
                        selected_index = int(body) - 1
                        vacant_houses = Houses.objects.filter(vacancy='VACANT')
                        selected_house = vacant_houses[selected_index]
                        state.selected_house_id = selected_house.id
                        state.state = 'awaiting_user_registration'
                        state.save()
                        response.message(f"You have selected house H({selected_house.id}). Please provide your Firstname, Lastname and email address: \n\n In the form Firstname, Lastname, Email. or 'Quit' ")
                    except (ValueError, IndexError):
                        response.message("Invalid selection. Please select a house by number from the list.")

            elif state.state == 'awaiting_user_registration':
                if body.lower() == 'quit':
                    response.message("You have ended the conversation. Have a great day!")
                    state.delete()
                else:
                    # Here you'd collect the user's information in stages, updating state after each step
                    # For brevity, let's assume the user is providing all information at once in a comma-separated format: "Firstname, Lastname, Email"
                    try:
                        # Splitting the input into first name, last name, and email
                        firstname, lastname, email = [part.strip() for part in body.split(',')]
                        
                        # Validate the presence of first name, last name, and email
                        if not firstname or not lastname or not email:
                            raise ValueError("Provide your information in the format: Firstname, Lastname, Email.")

                        # Email specific validation
                        if '@gmail.com' not in email.lower():
                            raise ValueError("Please provide a valid email address with '@gmail.com'.")
                        
                        # Check if email is already taken
                        if Customers.objects.filter(email=email).exists():
                            raise ValueError("The email address you provided is already taken by another user.")
                        
                        tenant = Customers.objects.create(
                            phone=sender,
                            firstname=firstname.strip(),
                            lastname=lastname.strip(),
                            email=email.strip(),
                            is_active = 1,
                            assigned_house_id = state.selected_house_id
                        )
                        
                        selected_house = Houses.objects.get(id=state.selected_house_id)

                        # Check if the selected house is still vacant
                        if selected_house.vacancy.lower() == 'vacant':
                            # Create the Assignment object
                            assignment = Assignment(tenant=tenant, house=selected_house)

                            selected_house.vacancy = 'OCCUPIED'  # logic to 'book' a house
                            selected_house.save()
                            
                            # Save the Assignment object, which updates the House vacancy status
                            assignment.save()
                            generate_invoices(request)
                            
                            response.message(f"Thank you {firstname.strip()}, you have been registered and your house has been booked.")
                            state.delete()  # Clean up the state after registration
                        else:
                            response.message("The house you selected is no longer available. Please start over.")
                            state.state = 'awaiting_house_interest'
                            state.save()
                    except ValueError as e:
                        response.message(str(e) + "\n")
                    except Houses.DoesNotExist:
                        response.message("The house you selected is no longer available. Please start over.")
                        state.state = 'awaiting_house_interest'
                        state.save()
        return HttpResponse(str(response), content_type='application/xml', status=200)
    else:
        return HttpResponse("Method Not Allowed", status=405)


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

    context = {'tenants': tenants,'form': form, 'assignments': assignments, 'page_house': page_house,'index_offset': index_offset,}
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
            Houses.objects.create(house_type = house_type, address = address, city = city, House_rent = House_rent, vacancy = vacancy)
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

    data = { 'id':house.id,'address': house.address, 'city': house.city,'rent': house.House_rent,'house_type': house.house_type,'status': house.vacancy}     
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
    context = {'cus': customer,'houses': houses,'index_offset' : index_offset,}
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
            Customers.objects.create{firstname = firstname,lastname = lastname, email = email, phone = 'whatsapp:' +'+254'+phone, is_active = active )
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

    data = {'id':customer.id,'firstname': customer.firstname,'lastname': customer.lastname,'email': customer.email,'phone': customer.phone,'active': customer.is_active}    
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
        messages.success(request, 'Link has been sent successfully')
        return payment_link
    except Invoice.DoesNotExist:
        messages.error(request, 'Invoice does not exist')
    return redirect('invoice_list')

def generate_invoices(request):
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
