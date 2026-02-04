import random
from rest_framework import status, views, permissions
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth import authenticate, get_user_model
from drf_spectacular.utils import extend_schema
from .models import Hotel, Flight
from .serializers import (
    UserProfileSerializer, VerifyOTPSerializer, 
    ResetPasswordSerializer, OTPSerializer,
    HotelListSerializer, FlightListSerializer, RentalCarListSerializer, HolidayPackageListSerializer, CruiseListSerializer
)

User = get_user_model()

class GlobalAuthPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        is_auth_required = getattr(settings, 'GLOBAL_AUTH_REQUIRED', True)
        if not is_auth_required:
            return True
        return request.user and request.user.is_authenticated

def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }



# 1. Send OTP (Unified for Signup/Signin)
class SendOTPView(views.APIView):
    permission_classes = [permissions.AllowAny]

    @extend_schema(request=OTPSerializer, responses={200: dict})
    def post(self, request):
        serializer = OTPSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            otp = str(random.randint(100000, 999999))
            
            user, created = User.objects.get_or_create(email=email)
            user.otp = otp
            user.save()

            send_mail(
                'Your OTP Code',
                f'Your OTP code is {otp}',
                settings.EMAIL_HOST_USER,
                [email],
                fail_silently=False,
            )
            return Response({'message': 'OTP sent successfully'}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# 2. Verify OTP
class VerifyOTPView(views.APIView):
    permission_classes = [permissions.AllowAny]

    @extend_schema(request=VerifyOTPSerializer, responses={200: dict})
    def post(self, request):
        serializer = VerifyOTPSerializer(data=request.data)
        if serializer.is_valid():
            otp = serializer.validated_data['otp']
            try:
                # Finding user by OTP
                user = User.objects.get(otp=otp)
                user.is_email_verified = True
                user.otp = None
                user.save()
                
                tokens = get_tokens_for_user(user)
                response_data = {
                    'message': 'OTP verified successfully.',
                    'tokens': tokens,
                    'is_onboarding_completed': user.is_onboarding_completed
                }

                # If onboarding is completed, include user details
                if user.is_onboarding_completed:
                    response_data['user_details'] = {
                        'first_name': user.first_name,
                        'last_name': user.last_name,
                        'phone_number': user.phone_number,
                        'address': user.address,
                        'email': user.email
                    }

                return Response(response_data, status=status.HTTP_200_OK)
            except User.DoesNotExist:
                return Response({'error': 'Invalid OTP or Email'}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# 3. Complete Onboarding
class CompleteOnboardingView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(request=UserProfileSerializer, responses={200: dict})
    def post(self, request):
        serializer = UserProfileSerializer(data=request.data)
        if serializer.is_valid():
            user = request.user
            user.first_name = serializer.validated_data['first_name']
            user.last_name = serializer.validated_data['last_name']
            user.phone_number = serializer.validated_data['phone_number']
            user.address = serializer.validated_data.get('address', user.address)
            user.is_onboarding_completed = True
            user.save()
            return Response({
                'message': 'Profile updated successfully', 
                'is_onboarding_completed': user.is_onboarding_completed
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)





#Forgot Password after send otp
class ForgotPasswordView(views.APIView):
    permission_classes = [permissions.AllowAny]

    @extend_schema(request=ResetPasswordSerializer, responses={200: dict})
    def post(self, request):
        serializer = ResetPasswordSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            otp = serializer.validated_data['otp']
            new_password = serializer.validated_data['new_password']
            try:
                user = User.objects.get(email=email, otp=otp)
                user.set_password(new_password)
                user.otp = None
                user.save()
                return Response({'message': 'Password reset successful'}, status=status.HTTP_200_OK)
            except User.DoesNotExist:
                return Response({'error': 'Invalid OTP or Email'}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)






#Now this api's are the Ticek hub main 5 api's

#1.Hotel api
class HotelListView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]  #[GlobalAuthPermission]

    @extend_schema(request=HotelListSerializer, responses={201: dict})
    def post(self, request):
        serializer = HotelListSerializer(data=request.data)
        if serializer.is_valid():
            instance = serializer.save(user=request.user)
            # Re-serialize to include auto-populated fields in response
            response_serializer = HotelListSerializer(instance)
            return Response({'message': 'Hotel search saved successfully', 'data': response_serializer.data}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


#2.Flight api
class FlightListView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]  #[GlobalAuthPermission]

    @extend_schema(request=FlightListSerializer, responses={201: dict})
    def post(self, request):
        serializer = FlightListSerializer(data=request.data)
        if serializer.is_valid():
            instance = serializer.save(user=request.user)
            # Re-serialize to include auto-populated fields in response
            response_serializer = FlightListSerializer(instance)
            return Response({'message': 'Flight search saved successfully', 'data': response_serializer.data}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)     


#3.Rental Car api


class RentalCarListView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]  #[GlobalAuthPermission]

    @extend_schema(request=RentalCarListSerializer, responses={201: dict})
    def post(self, request):
        serializer = RentalCarListSerializer(data=request.data)
        if serializer.is_valid():
            instance = serializer.save(user=request.user)
            # Re-serialize to include auto-populated fields in response
            response_serializer = RentalCarListSerializer(instance)
            return Response({'message': 'Rental Car search saved successfully', 'data': response_serializer.data}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)     


#4.Holiday Package api

class HolidayPackageListView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]  #[GlobalAuthPermission]

    @extend_schema(request=HolidayPackageListSerializer, responses={201: dict})
    def post(self, request):
        serializer = HolidayPackageListSerializer(data=request.data)
        if serializer.is_valid():
            instance = serializer.save(user=request.user)
            # Re-serialize to include auto-populated fields in response
            response_serializer = HolidayPackageListSerializer(instance)
            return Response({'message': 'Holiday Package search saved successfully', 'data': response_serializer.data}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


#5.Cruise api

class CruiseListView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]      #[GlobalAuthPermission]

    @extend_schema(request=CruiseListSerializer, responses={201: dict})
    def post(self, request):
        serializer = CruiseListSerializer(data=request.data)
        if serializer.is_valid():
            instance = serializer.save(user=request.user)
            # Re-serialize to include auto-populated fields in response
            response_serializer = CruiseListSerializer(instance)
            return Response({'message': 'Cruise search saved successfully', 'data': response_serializer.data}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


