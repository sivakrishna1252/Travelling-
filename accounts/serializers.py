from rest_framework import serializers
from .models import Hotel, Flight,RentalCar, HolidayPackage, Cruise

#authentication serializers
class UserRegisterSerializer(serializers.Serializer):
    first_name = serializers.CharField(max_length=100)
    last_name = serializers.CharField(max_length=100)
    email = serializers.EmailField()
    phone_number = serializers.CharField(max_length=15)
    address = serializers.CharField()

class UserProfileSerializer(serializers.Serializer):
    first_name = serializers.CharField(max_length=100)
    last_name = serializers.CharField(max_length=100)
    phone_number = serializers.CharField(max_length=15)
    address = serializers.CharField(style={'base_template': 'textarea.html'})

class VerifyOTPSerializer(serializers.Serializer):
    otp = serializers.CharField(max_length=6)

class UserLoginSerializer(serializers.Serializer):
    otp = serializers.CharField(max_length=6)

class ResetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField(max_length=6)
    new_password = serializers.CharField(write_only=True)

class OTPSerializer(serializers.Serializer):
    email = serializers.EmailField()




#main api's serializers

#Hotel serializer
class HotelSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(source='user.email', read_only=True)

    class Meta:
        model = Hotel
        fields = ['id', 'place', 'checkin_date', 'checkout_date', 'adults', 'children', 'rooms', 'customer_name', 'phone_number', 'user', 'user_email', 'coupon']
        read_only_fields = ['user', 'coupon', 'customer_name', 'phone_number']

class HotelListSerializer(serializers.ModelSerializer):
    checkin_date = serializers.DateField(help_text="Format: YYYY-MM-DD")
    checkout_date = serializers.DateField(help_text="Format: YYYY-MM-DD")
    childrens = serializers.IntegerField(source='children', default=0)
    adults = serializers.IntegerField()
    rooms = serializers.IntegerField()

    class Meta:
        model = Hotel
        fields = ['customer_name', 'phone_number', 'place', 'checkin_date', 'checkout_date', 'adults', 'childrens', 'rooms', 'coupon']
        read_only_fields = ['coupon', 'customer_name', 'phone_number']



#Flight serializer

class FlightSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(source='user.email', read_only=True)

    class Meta:
        model = Flight
        fields = ['id', 'from_location', 'to_location', 'round_trip', 'one_way', 'departure_date', 'return_date', 'adults', 'children', 'customer_name', 'phone_number', 'user', 'user_email', 'coupon']
        read_only_fields = ['user', 'coupon', 'customer_name', 'phone_number']


class FlightListSerializer(serializers.ModelSerializer):
    departure_date = serializers.DateField(help_text="Format: YYYY-MM-DD", required=False)
    return_date = serializers.DateField(help_text="Format: YYYY-MM-DD", required=False)
    childrens = serializers.IntegerField(source='children', default=0)
    adults = serializers.IntegerField()

    class Meta:
        model = Flight
        fields = ['customer_name', 'phone_number', 'from_location', 'to_location', 'round_trip', 'one_way', 'departure_date', 'return_date', 'adults', 'childrens', 'coupon']
        read_only_fields = ['coupon', 'customer_name', 'phone_number']


#Rental Car serializer

class RentalCarSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(source='user.email', read_only=True)

    class Meta:
        model = RentalCar
        fields = ['id', 'location', 'pickup_time', 'dropoff_time', 'customer_name', 'phone_number', 'user', 'user_email', 'coupon']
        read_only_fields = ['user', 'coupon', 'customer_name', 'phone_number']


class RentalCarListSerializer(serializers.ModelSerializer):
    pickup_time = serializers.DateTimeField(help_text="Format: YYYY-MM-DD HH:MM:SS")
    dropoff_time = serializers.DateTimeField(help_text="Format: YYYY-MM-DD HH:MM:SS")
  
    class Meta:
        model = RentalCar
        fields = ['customer_name', 'phone_number', 'location', 'pickup_time', 'dropoff_time',  'coupon']
        read_only_fields = ['coupon', 'customer_name', 'phone_number']



#Holiday Package serializer

class HolidayPackageSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(source='user.email', read_only=True)

    class Meta:
        model = HolidayPackage
        fields = ['id', 'to_location', 'from_location', 'duration', 'adults', 'children', 'customer_name', 'phone_number', 'user', 'user_email', 'coupon']
        read_only_fields = ['user', 'coupon', 'customer_name', 'phone_number']


class HolidayPackageListSerializer(serializers.ModelSerializer):
    duration = serializers.IntegerField()
    adults = serializers.IntegerField()
    children = serializers.IntegerField()

    class Meta:
        model = HolidayPackage
        fields = ['customer_name', 'phone_number', 'to_location', 'from_location', 'duration', 'adults', 'children', 'coupon']
        read_only_fields = ['coupon', 'customer_name', 'phone_number']


#Cruise serializer
class CruiseSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(source='user.email', read_only=True)

    class Meta:
        model = Cruise
        fields = ['id', 'to_location', 'from_location', 'duration', 'cabins', 'adults', 'children', 'customer_name', 'phone_number', 'user', 'user_email', 'coupon']
        read_only_fields = ['user', 'coupon', 'customer_name', 'phone_number']


class CruiseListSerializer(serializers.ModelSerializer):
    duration = serializers.IntegerField()
    cabins = serializers.CharField()
    adults = serializers.IntegerField()
    childrens = serializers.IntegerField(source='children', default=0)

    class Meta:
        model = Cruise
        fields = ['customer_name', 'phone_number', 'to_location', 'from_location', 'duration', 'cabins', 'adults', 'childrens', 'coupon']
        read_only_fields = ['coupon', 'customer_name', 'phone_number']
