#django model ko json me convert karna serialization
#json data ko python ke model me convert karna deserialization

from rest_framework import serializers
from .models import *

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model=Category
        fields=['id','category_name','creation_date']


class FoodSerializer(serializers.ModelSerializer):
    category_name=serializers.CharField(source='category.category_name',read_only=True)  # yeh alag se bhejna pad raha kyuki model se sirf id aa rahi 
    image=serializers.ImageField(required=False)
    is_available=serializers.BooleanField(required=False,default=True)
    class Meta:
        model=Food
        fields=['id','category','category_name','item_name','item_price','item_description','image','item_quantity','is_available']


class CartOrderSerializer(serializers.ModelSerializer):
    food= FoodSerializer()
    class Meta:
        model=Orders
        fields=['id','food','quantity']

class MyOrdersListSerializer(serializers.ModelSerializer):
    order_final_status=serializers.SerializerMethodField()
    class Meta:
        model=OrdersAddress
        fields=['order_number','order_time','order_final_status']    

    def get_order_final_status(self,obj):
        return obj.order_final_status or "Waiting for Restaurant Confirmation"    
    
class OrderSerializer(serializers.ModelSerializer):
    food= FoodSerializer()
    class Meta:
        model=Orders
        fields=['food','quantity']  

class OrderAddressSerializer(serializers.ModelSerializer):
    payment_mode=serializers.SerializerMethodField()

    class Meta:
        model=OrdersAddress
        fields=['order_number','address','order_time','order_final_status','payment_mode']    

    def get_payment_mode(self,obj):
        try :
           payment= PaymentDetail.objects.get(order_number=obj.order_number)
           return payment.payment_mode 
        except PaymentDetail.DoesNotExist:
            return None            