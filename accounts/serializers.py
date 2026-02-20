from rest_framework import serializers
from .models import Hotel, Flight, RentalCar, HolidayPackage, Cruise, MultiCityFlight, MultiCityFlightLeg

class ContactSupportSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=255, required=True, error_messages={'required': 'Please provide your name.'})
    email = serializers.EmailField(required=True, error_messages={
        'required': 'Email address is required.',
        'invalid': 'Please enter a valid email address (e.g., user@example.com).'
    })
    subject = serializers.CharField(max_length=255, required=True, error_messages={'required': 'Subject is required.'})
    message = serializers.CharField(required=True, error_messages={'required': 'Please enter your message.'})

# ... other serializers ...

# Multi-City Flight serializer
class MultiCityFlightLegSerializer(serializers.ModelSerializer):
    class Meta:
        model = MultiCityFlightLeg
        fields = ['from_location', 'to_location', 'departure_date']

class MultiCityFlightSerializer(serializers.ModelSerializer):
    legs = MultiCityFlightLegSerializer(many=True)
    childrens = serializers.IntegerField(source='children', default=0)

    class Meta:
        model = MultiCityFlight
        fields = ['customer_name', 'phone_number', 'adults', 'childrens', 'coupon', 'legs']
        read_only_fields = ['coupon', 'customer_name', 'phone_number']

    def create(self, validated_data):
        legs_data = validated_data.pop('legs')
        multi_city_flight = MultiCityFlight.objects.create(**validated_data)
        for leg_data in legs_data:
            MultiCityFlightLeg.objects.create(multi_city_flight=multi_city_flight, **leg_data)
        return multi_city_flight

    def validate(self, data):
        adults = data.get('adults', 0)
        children = data.get('children', 0)
        if adults == 0 and children == 0:
            raise serializers.ValidationError("Either adults or children must be at least 1.")
        
        legs = data.get('legs', [])
        if not legs:
            raise serializers.ValidationError("At least one flight leg is required for multi-city flights.")
        
        return data


#authentication serializers
class UserRegisterSerializer(serializers.Serializer):
    first_name = serializers.CharField(max_length=100)
    last_name = serializers.CharField(max_length=100)
    phone_number = serializers.CharField(max_length=15)
    address = serializers.CharField()

class UserProfileSerializer(serializers.Serializer):
    first_name = serializers.CharField(max_length=50, required=True, allow_blank=False)
    last_name = serializers.CharField(max_length=50, required=True, allow_blank=False)
    phone_number = serializers.CharField(max_length=15, required=True, allow_blank=False)
    address = serializers.CharField(required=True, allow_blank=False)

    def validate_phone_number(self, value):
        if not value.isdigit():
            raise serializers.ValidationError("Phone number must contain only digits.")
        if len(value) < 10 or len(value) > 15:
            raise serializers.ValidationError("Phone number must be between 10 and 15 digits.")
        return value

class VerifyOTPSerializer(serializers.Serializer):
    email = serializers.EmailField()
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
    checkin_date = serializers.DateField(required=True, help_text="Format: YYYY-MM-DD")
    checkout_date = serializers.DateField(required=True, help_text="Format: YYYY-MM-DD")
    childrens = serializers.IntegerField(source='children', default=0)
    adults = serializers.IntegerField(default=0)
    rooms = serializers.IntegerField(default=0)
    place = serializers.CharField(required=True)

    class Meta:
        model = Hotel
        fields = ['customer_name', 'phone_number', 'place', 'checkin_date', 'checkout_date', 'adults', 'childrens', 'rooms', 'coupon']
        read_only_fields = ['coupon', 'customer_name', 'phone_number']

    def validate(self, data):
        # Mandatory traveler check
        adults = data.get('adults', 0)
        children = data.get('children', 0)
        if adults == 0 and children == 0:
            raise serializers.ValidationError("Either adults or children must be at least 1.")
        
        # Explicit Room Check (prevent default 0)
        rooms = data.get('rooms', 0)
        if rooms < 1:
            raise serializers.ValidationError({"rooms": "Please select at least 1 room."})
            
        return data



#Flight serializer

class FlightSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(source='user.email', read_only=True)

    class Meta:
        model = Flight
        fields = ['id', 'from_location', 'to_location', 'round_trip', 'one_way', 'departure_date', 'return_date', 'adults', 'children', 'customer_name', 'phone_number', 'user', 'user_email', 'coupon']
        read_only_fields = ['user', 'coupon', 'customer_name', 'phone_number']


class FlightListSerializer(serializers.ModelSerializer):
    from_location = serializers.CharField(required=True)
    to_location = serializers.CharField(required=True)
    departure_date = serializers.DateField(help_text="Format: YYYY-MM-DD", required=False)
    return_date = serializers.DateField(help_text="Format: YYYY-MM-DD", required=False)
    childrens = serializers.IntegerField(source='children', default=0)
    adults = serializers.IntegerField(default=0)

    class Meta:
        model = Flight
        fields = ['customer_name', 'phone_number', 'from_location', 'to_location', 'round_trip', 'one_way', 'departure_date', 'return_date', 'adults', 'childrens', 'coupon']
        read_only_fields = ['coupon', 'customer_name', 'phone_number']

    def validate(self, data):
        # Mandatory traveler check
        adults = data.get('adults', 0)
        children = data.get('children', 0)
        if adults == 0 and children == 0:
            raise serializers.ValidationError("Either adults or children must be at least 1.")

        # Trip type mutual exclusivity
        round_trip = data.get('round_trip', False)
        one_way = data.get('one_way', False)
        if round_trip and one_way:
            raise serializers.ValidationError("Please select either One Way or Round Trip, not both.")
        if not round_trip and not one_way:
            raise serializers.ValidationError("Please select either One Way or Round Trip.")

        # Trip logic
        departure_date = data.get('departure_date')
        return_date = data.get('return_date')

        if not departure_date:
            raise serializers.ValidationError({"departure_date": "Departure date is required."})

        if round_trip and not return_date:
            raise serializers.ValidationError({"return_date": "Return date is required for round trips."})

        return data


#Rental Car serializer

class RentalCarSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(source='user.email', read_only=True)

    class Meta:
        model = RentalCar
        fields = ['id', 'location', 'pickup_time', 'dropoff_time', 'customer_name', 'phone_number', 'user', 'user_email', 'coupon']
        read_only_fields = ['user', 'coupon', 'customer_name', 'phone_number']


class RentalCarListSerializer(serializers.ModelSerializer):
    location = serializers.CharField(required=True)
    pickup_time = serializers.DateTimeField(required=True, help_text="Format: YYYY-MM-DD HH:MM:SS")
    dropoff_time = serializers.DateTimeField(required=True, help_text="Format: YYYY-MM-DD HH:MM:SS")
  
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
    to_location = serializers.CharField(required=True)
    from_location = serializers.CharField(required=True)
    duration = serializers.IntegerField(default=0)
    adults = serializers.IntegerField(default=0)
    children = serializers.IntegerField(default=0)

    class Meta:
        model = HolidayPackage
        fields = ['customer_name', 'phone_number', 'to_location', 'from_location', 'duration', 'adults', 'children', 'coupon']
        read_only_fields = ['coupon', 'customer_name', 'phone_number']

    def validate(self, data):
        # Mandatory traveler check
        adults = data.get('adults', 0)
        children = data.get('children', 0)
        if adults == 0 and children == 0:
            raise serializers.ValidationError("Either adults or children must be at least 1.")
        
        # Explicit Duration Check
        duration = data.get('duration', 0)
        if duration < 1:
            raise serializers.ValidationError({"duration": "Duration must be at least 1 day."})

        return data


#Cruise serializer
class CruiseSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(source='user.email', read_only=True)

    class Meta:
        model = Cruise
        fields = ['id', 'to_location', 'from_location', 'duration', 'cabins', 'adults', 'children', 'customer_name', 'phone_number', 'user', 'user_email', 'coupon']
        read_only_fields = ['user', 'coupon', 'customer_name', 'phone_number']


class CruiseListSerializer(serializers.ModelSerializer):
    to_location = serializers.CharField(required=True)
    from_location = serializers.CharField(required=True)
    duration = serializers.IntegerField(default=0)
    cabins = serializers.CharField(required=True, allow_blank=False)
    adults = serializers.IntegerField(default=0)
    childrens = serializers.IntegerField(source='children', default=0)

    class Meta:
        model = Cruise
        fields = ['customer_name', 'phone_number', 'to_location', 'from_location', 'duration', 'cabins', 'adults', 'childrens', 'coupon']
        read_only_fields = ['coupon', 'customer_name', 'phone_number']

    def validate(self, data):
        # Mandatory traveler check
        adults = data.get('adults', 0)
        children = data.get('children', 0)
        if adults == 0 and children == 0:
            raise serializers.ValidationError("Either adults or children must be at least 1.")
        
        # Explicit Duration Check
        duration = data.get('duration', 0)
        if duration < 1:
            raise serializers.ValidationError({"duration": "Duration must be at least 1 day."})
            
        return data
