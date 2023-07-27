from django.shortcuts import render, redirect
from django.shortcuts import reverse
from .models import *
from .models import Prodcut
from django.contrib import messages
from django.http import JsonResponse
from django.core import serializers
from django.http import HttpResponse
from django.utils import timezone
from datetime import timedelta
from django.views.decorators.csrf import csrf_exempt
import json


# This function renders the homepage
def homepage(request):
    return render(request, 'homepage.html')

# This function displays all the info about a specific USER on a page with the corresponding ID
def profile(request):
    user = check_session(request)
    context = {
        'user': user,
    }
    return render(request, 'users-profile.html', context)
# This function edit the profile info
def edit(request):
    errors = User.objects.editValidator(request.POST)
    if len(errors) > 0:
        for key, value in errors.items():
            messages.error(request, value)
        return redirect('/dashboard/profile')
    else:
        selected = User.objects.get(id=request.session['user'])
        selected.f_name = request.POST['f_name']
        selected.l_name = request.POST['l_name']
        selected.s_name = request.POST['s_name']
        selected.email = request.POST['email']
        selected.save()
        return redirect('/dashboard/profile')
#This function renders the page that displays all products in the database
def prodcuts(request):
    products = Prodcut.objects.all()
    context = {
        'products' : products
    }
    return render(request, 'products-page.html', context)

################## Registration and Loging ################
#This function renders the sign up page upon button click
def signup_page(request):
    return render(request, 'pages-register2.html')

#This function for registration process
def register(request):
    errors = User.objects.regValidator(request.POST)
    if len(errors) > 0:
        for key, value in errors.items():
            messages.error(request, value)
        return redirect('/signup')
    else:
        User.objects.create(
        f_name= request.POST['f_name'], 
        l_name= request.POST['l_name'], 
        s_name= request.POST['s_name'], 
        email=request.POST['email'], 
        password=request.POST['password'])
        return render(request, 'pages-login-2.html')

#This function renders the Log In page upon button click
def signin_page(request):
    return render(request, 'pages-login-2.html')

#This function for loging process
def login(request):
    errors = User.objects.loginValidator(request.POST)
    if len(errors) > 0:
        for key, value in errors.items():
            messages.error(request, value)
        return render(request, 'pages-login-2.html')
    else:
        user = User.objects.get(email = request.POST['email'])
        request.session['user'] = user.id
        request.session['username'] = user.f_name
        print('user')
        return redirect('/dashboard')
    
# ------------------ KAREEM SECTION START ---------------------------
#Page : Order Page
def order_page(request):
    user = check_session(request)
    context = {
        'user' : user
    }
    return render(request,'orders_page.html',context)

def is_ajax(request):
    return request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest'

#Process: Order list
def order_list_process(request):

    try:
        if is_ajax(request = request) and request.method == "POST":
            # Check if the barcode is exist
            product = Prodcut.objects.filter(p_barcode=request.POST['barcode']).first()

            order_list_qty = request.POST['product_qty'] 
            order_list_price = request.POST['product_price'] 
            barcode = product.p_barcode

            Order_list.objects.create(p_price=order_list_price,
                                    qty_sell=order_list_qty,
                                    products=product.p_name,
                                    p_barcode = barcode)
            return JsonResponse({'message': 'Success'})
    except:
        return JsonResponse({'message': 'Invalid request '})


def get_order_list(request):
    order_list = Order_list.objects.all().values('id','p_price', 'qty_sell', 'products', 'p_barcode')
    return JsonResponse({"order_list":list(order_list)})

# Process: Delete
def remove_order_list(request,order_id):
    order_list = Order_list.objects.get(id=order_id)
    order_list.delete()
    return JsonResponse({'message': 'Success'})

# ------------------ KAREEM SECTION START ---------------------------


#This function renders the "add new product" form
def add_product(request):
    return render(request, 'add_product.html')

#This function handles POST data from "add new product" form and adds new PRODUCT to db:
def save_product(request):
    if request.method == 'POST':
        params = dict()
        
        params['p_name'] = request.POST.get('p_name')
        params['p_barcode'] = request.POST.get('p_barcode')
        params['expire_date'] = request.POST.get('expire_date')
        params['cost'] = request.POST.get('cost')
        params['qty'] = request.POST.get('qty')
        print(params['cost'])
        
        Prodcut.objects.create(**params)

    return redirect(reverse('products-page'))

#------------------------`````````Update 2 KAREEM -----------------------
# Process: process_order
def process_order(request):
    # Get the objects from the order_list
    order_list = Order_list.objects.all()
    # Add the objects in the order_list to the order Table*
    user = User.objects.get(id=request.session['user'])
    for order in order_list:
        Order.objects.create(p_price = order.p_price, qty_sell = order.qty_sell, products = order.products ,p_barcode = order.p_barcode, user = user)
    # Delete the order_list items
    order_list_delete_all()
    return redirect('/order_page')


# Function: Delete all the records at the order_list table
def order_list_delete_all():
    Order_list.objects.all().delete()
    return

# Process: Clear order_list Items
def clear_all_order_list_process(request):
    order_list_delete_all()
    return redirect('/order_page')

# Process: Logout
def logout_process(request):
    request.session.flush()
    return redirect('/')

# Function : Check Session
def check_session(request):
    if request.session.has_key('user') == True:
        user_session = User.objects.get(id=request.session['user'])
    else:
        user_session = False
    return user_session

#--------------------------------- Kareem Update 3:-------------------------------
# Process : Delete Product from the DB
def remove_product_process(request,product_id):
    product = Prodcut.objects.get(id=product_id)
    product.delete()
    return redirect('/dashboard')

# Page: Display Orders Page
def display_orders_page(request):
    user = check_session(request)
    if user:
        orders=Order.objects.filter(user=user)
    context = {
        'orders' : orders,
        'user' : user,
    }
    return render(request,'display_orders_page.html',context)

#--------------------------------- Kareem Update 4:-------------------------------
def  products_total_qty(products):

    product_qty_dictionary = {}
    filtered_list = []
    # Iterate through the products list
    for item in products:
        # Check the 'product_qty_dictionary' dictionary if it contains that product so dose not iterate again because we already have its value
        # If this product name dose not exists bring all the products with that name
        if (str(item.p_name) in product_qty_dictionary) == False:
            total = 0
            # get all the products that have the same name as this product
            filtered_products = Prodcut.objects.filter(p_name = item.p_name)
            # Iterate through all products and get the total qty
            for product in filtered_products:
                total += product.qty
            # Add a new attribute to the product object called total_qty : value = total
            setattr(item,'total_qty',total)
            # Add this product name to 'product_qty_dictionary' dictionary and its value so next time if the same product came we don't
            # repeat this process
            product_qty_dictionary[f"{item.p_name}"] = total
            # Add the product object with the new attribute to 'filtered_list'
            filtered_list.append(item)
        # if the product already exists in dictionary get its value from the dictionary
        else:
            setattr(item,'total_qty',product_qty_dictionary[item.p_name])
            filtered_list.append(item)
    # Return the filtered list of products objects containing total_qty
    return filtered_list


# ********************* THIS IS THE CALCULATION PART ***************** #
# This function displays the dashboard to the user with calculations functions:
def dashboard(request):
    current_date = timezone.now().date()
    #products = Prodcut.objects.all()
    user = check_session(request)
    if user:
        if user:
            products = Prodcut.objects.filter(user=user)
        warning_products = []
        
        # This part displays products that will expire in [10 days] or less as a warning on the Dashboard:
        for product in products:
            days_delta = (product.expire_date.date() - current_date).days
            if days_delta <= 10:
                warning_products.append(product)
        # send list of products objects that want to add total available value to them 
        warning_products = products_total_qty(warning_products)
        
        #This part calculates the total cost of all available stock
        products = Prodcut.objects.filter(user=user)
        total_cost = 0
        formatted_total_cost = '0'

        for product in products:
            total_cost += product.qty * product.cost
            formatted_total_cost = "{:,.2f}".format(total_cost)


        #This part calculates the number of items in stock:
        #products = Prodcut.objects.all()
        orders = Order.objects.filter(user = user)

        total_qty = 0
        for product in products:
            total_qty += product.qty

        total_items_sold = 0

        for order in orders:
            total_qty -= order.qty_sell
            total_items_sold += order.qty_sell

        #This part calculates the total revenue from orders made in the past 30 days:
        thirty_days_ago = timezone.now() - timedelta(days=30)
        orders_last_30_days = orders.filter(created_at__gte = thirty_days_ago)
        totalValue_30days = 0
        formatted_totalValue_30days = 0
        
        for order in orders_last_30_days:
            totalValue_30days += order.totalValue
            formatted_totalValue_30days = "{:,.2f}".format(totalValue_30days)
    else:
        warning_products = formatted_total_cost = total_qty =total_items_sold =formatted_totalValue_30days = 0


    context = {
        'products': warning_products,
        'user' : user,
        'formatted_total_cost' : formatted_total_cost,
        'total_qty': total_qty,
        'total_items_sold' : total_items_sold,
        'formatted_totalValue_30days' : formatted_totalValue_30days,
    } 

    return render(request, 'dashboard.html', context)

# ********************* HAMADA SECTION ****************************
# This function displays the name of the user in the profile section
def display_products(request):
    context = {
        'user' : User.objects.get(id=request.session['user'])
    }
    return render(request, 'display_products-page.html', context)

# This function saves products 
def save_products(request):
    try:
        if request.method == 'POST':
            data = request.POST.get('data')
            try:
                products = json.loads(data)
                # Save products to the database
                for product in products:
                    new_product = Prodcut(
                        p_name=product['p_name'],
                        p_barcode=int(product['p_barcode']),
                        expire_date=product['expire_date'],
                        cost=int(product['cost']),
                        qty=int(product['qty']),
                        user=User.objects.get(id=request.session.get('user'))
                    )
                    new_product.save()

                return JsonResponse({'message': 'Products saved successfully'})
            except Exception as e:
                return JsonResponse({'error': 'Error saving products: ' + str(e)}, status=500)
    except Exception as e:
        return JsonResponse({'error': 'Invalid request method'}, status=400)
    

# This function displays all products that exist in the db:
def all_product(request):
    user = check_session(request)
    if user:
        products = Prodcut.objects.filter(user=user) 
    context = {
        'products' : products,
        'user' : user, 
    }
    return render(request, 'all_product.html', context)

# This function searches products in the db using their barcodes:
def search(request):
    search = request.POST['search']
    search = int(search)
    products = Prodcut.objects.all() #array 
    product_list = []
    for x in products: 
        if search == x.p_barcode: 
            product_list.append(x)
    print(product_list)
    context = {
        'prod_search' : product_list, 
    }
    return render(request, 'all_product.html', context)

