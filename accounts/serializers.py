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
    customer_name = serializers.CharField(source='display_name', read_only=True)

    class Meta:
        model = Hotel
        fields = ['id', 'place', 'date', 'adults', 'children', 'rooms', 'customer_name', 'user', 'user_email', 'coupon']
        read_only_fields = ['user', 'coupon']

class HotelListSerializer(serializers.ModelSerializer):
    date = serializers.DateField(help_text="Format: YYYY-MM-DD")
    childrens = serializers.IntegerField(source='children', default=0)
    adults = serializers.IntegerField()
    rooms = serializers.IntegerField()
    customer_name = serializers.CharField(source='display_name', read_only=True)

    class Meta:
        model = Hotel
        fields = ['customer_name', 'place', 'date', 'adults', 'childrens', 'rooms', 'coupon']
        read_only_fields = ['coupon']



#Flight serializer

class FlightSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(source='user.email', read_only=True)
    customer_name = serializers.CharField(source='display_name', read_only=True)

    class Meta:
        model = Flight
        fields = ['id', 'from_location', 'to_location', 'round_trip', 'one_way', 'departure_date', 'return_date', 'adults', 'children', 'user', 'user_email', 'coupon']
        read_only_fields = ['user', 'coupon']


class FlightListSerializer(serializers.ModelSerializer):
    departure_date = serializers.DateField(help_text="Format: YYYY-MM-DD", required=False)
    return_date = serializers.DateField(help_text="Format: YYYY-MM-DD", required=False)
    childrens = serializers.IntegerField(source='children', default=0)
    adults = serializers.IntegerField()
    customer_name = serializers.CharField(source='display_name', read_only=True)

    class Meta:
        model = Flight
        fields = ['customer_name', 'from_location', 'to_location', 'round_trip', 'one_way', 'departure_date', 'return_date', 'adults', 'childrens', 'coupon']
        read_only_fields = ['coupon']


#Rental Car serializer

class RentalCarSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(source='user.email', read_only=True)
    customer_name = serializers.CharField(source='display_name', read_only=True)

    class Meta:
        model = RentalCar
        fields = ['id', 'location', 'pickup_time', 'dropoff_time', 'adults', 'children', 'user', 'user_email', 'coupon']
        read_only_fields = ['user', 'coupon']


class RentalCarListSerializer(serializers.ModelSerializer):
    pickup_time = serializers.DateTimeField(help_text="Format: YYYY-MM-DD HH:MM:SS")
    dropoff_time = serializers.DateTimeField(help_text="Format: YYYY-MM-DD HH:MM:SS")
    childrens = serializers.IntegerField(source='children', default=0)
    adults = serializers.IntegerField()
    customer_name = serializers.CharField(source='display_name', read_only=True)

    class Meta:
        model = RentalCar
        fields = ['customer_name', 'location', 'pickup_time', 'dropoff_time', 'adults', 'childrens', 'coupon']
        read_only_fields = ['coupon']



#Holiday Package serializer

class HolidayPackageSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(source='user.email', read_only=True)
    customer_name = serializers.CharField(source='display_name', read_only=True)

    class Meta:
        model = HolidayPackage
        fields = ['id', 'to_location', 'from_location', 'duration', 'passengers', 'user', 'user_email', 'coupon']
        read_only_fields = ['user', 'coupon']


class HolidayPackageListSerializer(serializers.ModelSerializer):
    duration = serializers.IntegerField()
    passengers = serializers.IntegerField()
    customer_name = serializers.CharField(source='display_name', read_only=True)

    class Meta:
        model = HolidayPackage
        fields = ['customer_name', 'to_location', 'from_location', 'duration', 'passengers', 'coupon']
        read_only_fields = ['coupon']


#Cruise serializer

class CruiseSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(source='user.email', read_only=True)
    customer_name = serializers.CharField(source='display_name', read_only=True)

    class Meta:
        model = Cruise
        fields = ['id', 'to_location', 'from_location', 'duration', 'cabins', 'adults', 'children', 'user', 'user_email', 'coupon']
        read_only_fields = ['user', 'coupon']


class CruiseListSerializer(serializers.ModelSerializer):
    duration = serializers.IntegerField()
    cabins = serializers.IntegerField()
    adults = serializers.IntegerField()
    childrens = serializers.IntegerField(source='children', default=0)
    customer_name = serializers.CharField(source='display_name', read_only=True)

    class Meta:
        model = Cruise
        fields = ['customer_name', 'to_location', 'from_location', 'duration', 'cabins', 'adults', 'childrens', 'coupon']
        read_only_fields = ['coupon']
