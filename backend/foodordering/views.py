from django.shortcuts import render
from django.contrib.auth import authenticate
from rest_framework.decorators import api_view,parser_classes
from rest_framework.response import Response
from .models import *
# Create your views here.

@api_view(['POST'])
def admin_login_api(request):
     username=request.data.get('username')
     password=request.data.get('password')


     user=authenticate(username=username,password=password)   # waha par user table bani hogi usse match karta hai,provided by django to auth from superuser

     if user is not None and user.is_staff:
          return Response ({"message":"login succesfully","username":username},status=200)
     return Response({"message":"invalid credential"},status=401)


@api_view(['POST'])        # decorator hai method batate hai jab frontend se data fecth karna ho
def add_category(request):
     category_name=request.data.get('category_name')
     Category.objects.create(category_name=category_name)        # columnname=variable name
     return Response({"message":"category has been added"},status=201)

# yeh table me data lane ke liye hai backend se
from .serializers import *
@api_view(['GET'])        # decorator hai method batate hai jab frontend se data fecth karna ho
def list_category(request):
     categories=Category.objects.all()    # query to get all data from backend get,filter,all
     serializers=CategorySerializer(categories,many=True)
     return Response(serializers.data)


from rest_framework.parsers import MultiPartParser,FormParser
from .serializers import FoodSerializer

@api_view(['POST'])        # decorator hai method batate hai jab frontend se data fecth karna ho
@parser_classes([MultiPartParser,FormParser])
def add_food_item(request):
     serializer=FoodSerializer(data=request.data)
     if serializer.is_valid():
            serializer.save()
            return Response({"message":"Food item  has been added"},status=201)

     return  Response({"message":"Something went wrong"},status=400)



@api_view(['GET'])        # decorator hai method batate hai jab frontend se data fecth karna ho
def list_foods(request):
     foods=Food.objects.all()    # query to get all data from backend get,filter,all
     serializers=FoodSerializer(foods,many=True)
     return Response(serializers.data)

@api_view(['GET'])        # decorator hai method batate hai jab frontend se data fecth karna ho
def food_search(request):
     query=request.GET.get('q','')
     foods=Food.objects.filter(item_name__icontains=query)    # query to get all data from backend get,filter,all
     serializers=FoodSerializer(foods,many=True)
     return Response(serializers.data)

import random
@api_view(['GET'])        # decorator hai method batate hai jab frontend se data fecth karna ho
def random_foods(request):
     foods=list(Food.objects.all())    # query to get all data from backend get,filter,all
     random.shuffle(foods)
     limited_foods=foods[0:9]
     serializers=FoodSerializer(limited_foods,many=True)
     return Response(serializers.data)

from django.contrib.auth.hashers import make_password
@api_view(['POST'])        # decorator hai method batate hai jab frontend se data fecth karna ho

def register_user(request):
     firstname=request.data.get('firstname')
     lastname=request.data.get('lastname')
     mobile=request.data.get('mobilenumber')
     email=request.data.get('email')
     password=request.data.get('password')
     if User.objects.filter(email=email).exists() or User.objects.filter(mobile=mobile).exists():
            return Response({"message":"email or mobile number already registered"},status=400)
     User.objects.create(first_name=firstname,last_name=lastname,email=email,mobile=mobile,
                         password=make_password(password))
     return  Response({"message":"User registered successfully "},status=201)



from django.db.models import Q  # to apply multiple conditions 
from django.contrib.auth.hashers import check_password
@api_view(['POST'])        # decorator hai method batate hai jab frontend se data fecth karna ho

def login_user(request):
     identifier=request.data.get('emailcont')
     password=request.data.get('password')
     try :
          user = User.objects.get(Q(email=identifier) | Q(mobile=identifier))
          if check_password(password,user.password):
               return Response({"message":"Login Successsful","userId":user.id,"userName":f"{user.first_name} {user.last_name}"},status=200)
          else:
               return  Response({"message":"invalid credentials "},status=401)
     except:
           return  Response({"message":"invalid credentials "},status=401)
     
from django.shortcuts import get_object_or_404
@api_view(['GET'])        # decorator hai method batate hai jab frontend se data fecth karna ho
def food_detail(request,id):
     # foods=Food.objects.get(id=id)    # query to get all data from backend get,filter,all
     foods=get_object_or_404(Food,id=id) 
     serializers=FoodSerializer(foods)
     return Response(serializers.data)



@api_view(['POST'])        # decorator hai method batate hai jab frontend se data fecth karna ho

def add_to_cart(request):
     user_id=request.data.get('userId')
     food_id=request.data.get('foodId')
     try :
          user = User.objects.get(id=user_id)
          food = Food.objects.get(id=food_id)

          order,created=Orders.objects.get_or_create(
               user = user,
               food = food,
               is_order_placed = False,
               # quantity=1,
               defaults = {'quantity':1},
          )

          if not created:
               order.quantity+=1
               order.save()
          
          return Response({"message":"Food added to cart Successsfully"},status=200)
          
     except:
           return  Response({"message":"something went wrong "},status=404)


@api_view(['GET']) 
def get_cart_items(request,user_id):
    orders= Orders.objects.filter(user_id=user_id,is_order_placed=False).select_related('food')
    serializers=CartOrderSerializer(orders,many=True)
    return Response(serializers.data)

@api_view(['PUT']) 
def update_cart_quantity(request):
     order_id=request.data.get('OrderId')
     quantity=request.data.get('quantity')
     try :
          order = Orders.objects.get(id=order_id)
          order.quantity=quantity
          order.save()          
          return Response({"message":"qunatity updated successfully Successsfully"},status=200)
          
     except:
           return  Response({"message":"something went wrong "},status=404)

@api_view(['DELETE']) 
def delete_cart_item(request,order_id):
     
     try :
          order = Orders.objects.get(id=order_id,is_order_placed=False)
          order.delete()          
          return Response({"message":"Item deleted from cart"},status=200)
          
     except:
           return  Response({"message":"something went wrong "},status=404)
     
def make_unique_order_number():
     while True:
          num=str(random.randint(100000000,999999999))
          if (not OrdersAddress.objects.filter(order_number=num).exists()):
           return num

@api_view(['POST'])        # decorator hai method batate hai jab frontend se data fecth karna ho
def place_order(request):
     user_id=request.data.get('userId')
     address=request.data.get('address')
     payment_mode=request.data.get('paymentMode')
     card_number=request.data.get('cardNumber')
     expiry=request.data.get('expiry')
     cvv=request.data.get('cvv')
     try :
          order = Orders.objects.filter(user_id=user_id,is_order_placed=False)
          order_number=make_unique_order_number()
          order.update(order_number=order_number,is_order_placed=True)

          OrdersAddress.objects.create(
               user_id=user_id,
               order_number=order_number,
               address=address
          )

          PaymentDetail.objects.create(
             user_id=user_id,
             order_number=order_number,
             payment_mode=payment_mode,
             card_number=card_number if payment_mode == 'online' else None, 
             expiry_date=expiry if payment_mode == 'online' else None,
             cvv=cvv if payment_mode == 'online' else None, 
          )

          return Response({"message":f'order placed  Successsfully! Order no: {order_number}'},status=201)
          
     except:
           return  Response({"message":"something went wrong "},status=404)




@api_view(['GET']) 
def user_orders(request,user_id):
    orders= OrdersAddress.objects.filter(user_id=user_id).order_by('-id')
    serializers=MyOrdersListSerializer(orders,many=True)
    return Response(serializers.data)


@api_view(['GET']) 
def order_by_order_number(request,order_number):
    orders= Orders.objects.filter(order_number=order_number,is_order_placed=True).select_related('food')
    serializers=OrderSerializer(orders,many=True)
    return Response(serializers.data)


@api_view(['GET']) 
def get_order_address(request,order_number):
    address= OrdersAddress.objects.get(order_number=order_number)
    serializers=OrderAddressSerializer(address)
    return Response(serializers.data)

from django.shortcuts import render

def get_invoice(request,order_number):
     orders= Orders.objects.filter(order_number=order_number,is_order_placed=True).select_related('food')
     address= OrdersAddress.objects.get(order_number=order_number)

     grand_total=0
     order_data=[]

     for order in orders:
          total_price= order.food.item_price * order.quantity
          grand_total+=total_price

          order_data.append({
               'food' : order.food,
               'quantity' :order.quantity,
               'total_price' : total_price
          })

     return render (request,'invoice.html',{
              'order_number': order_number,
              
              'address': address,
              'grand_total':grand_total,
              'orders': order_data
          })