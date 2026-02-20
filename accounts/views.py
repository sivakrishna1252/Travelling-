import random
from rest_framework import status, views, permissions
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth import authenticate, get_user_model
from django.utils import timezone
from datetime import timedelta
from drf_spectacular.utils import extend_schema
from .models import Hotel, Flight, OTPLog, MultiCityFlight
from .serializers import (
    UserProfileSerializer, VerifyOTPSerializer, 
    ResetPasswordSerializer, OTPSerializer,
    HotelListSerializer, FlightListSerializer, RentalCarListSerializer, HolidayPackageListSerializer, CruiseListSerializer,
    MultiCityFlightSerializer, ContactSupportSerializer
)


User = get_user_model()

# --- Custom Permissions ---

class IsOnboardingCompletedPermission(permissions.BasePermission):
    """
    Allows access only to users who have completed their onboarding profile.
    """
    message = "You must complete your profile onboarding before accessing this feature."

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.is_onboarding_completed)

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

# --- Authentication Views ---

# 1. Send OTP
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
            user.otp_created_at = timezone.now()
            user.save()

            send_mail(
                'Your OTP Code',
                f'Your OTP code is {otp}',
                settings.EMAIL_HOST_USER,
                [email],
                fail_silently=False,
            )
            # Log the OTP attempt
            OTPLog.objects.create(
                user=user,
                phone_number=email, # Using email since it's the primary identifier
                otp_code=otp,
                is_successful=False # Initially False until verified
            )

            return Response({'message': 'OTP sent successfully'}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# 2. Verify OTP (Unified Login/Signup)
class VerifyOTPView(views.APIView):
    permission_classes = [permissions.AllowAny]

    @extend_schema(request=VerifyOTPSerializer, responses={200: dict})
    def post(self, request):
        serializer = VerifyOTPSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            otp = serializer.validated_data['otp']
            try:
                user = User.objects.get(email=email, otp=otp)
                
                if user.otp_created_at:
                    expiry_time = user.otp_created_at + timedelta(minutes=2)
                    if timezone.now() > expiry_time:
                        return Response({'error': 'OTP has expired'}, status=status.HTTP_400_BAD_REQUEST)

                # Reset OTP and activate user
                user.is_email_verified = True
                user.otp = None
                user.otp_created_at = None
                if not user.is_active:
                    user.is_active = True
                user.save()
                
                # Log success in the history
                OTPLog.objects.filter(user=user, otp_code=otp).update(is_successful=True)
                
                # Always return tokens to maintain session
                tokens = get_tokens_for_user(user)
                
                response_data = {
                    'message': 'OTP verified successfully.',
                    'tokens': tokens,
                    'is_onboarding_completed': user.is_onboarding_completed
                }

                if user.is_onboarding_completed:
                    response_data['user_details'] = {
                        'first_name': user.first_name,
                        'last_name': user.last_name,
                        'phone_number': user.phone_number,
                        'address': user.address,
                        'email': user.email
                    }
                else:
                    response_data['message'] = 'OTP verified. Please complete onboarding to gain full access.'

                return Response(response_data, status=status.HTTP_200_OK)
            except User.DoesNotExist:
                return Response({'error': 'Invalid OTP or Email'}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# 3. Complete Onboarding
class CompleteOnboardingView(views.APIView):
    # Requires tokens from VerifyOTPView
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(request=UserProfileSerializer, responses={200: dict})
    def post(self, request):
        user = request.user
        
        if user.is_onboarding_completed:
            return Response({'error': 'Onboarding already complete'}, status=status.HTTP_400_BAD_REQUEST)

        serializer = UserProfileSerializer(data=request.data)
        if serializer.is_valid():
            user.first_name = serializer.validated_data['first_name']
            user.last_name = serializer.validated_data['last_name']
            user.phone_number = serializer.validated_data['phone_number']
            user.address = serializer.validated_data.get('address', user.address)
            user.is_onboarding_completed = True
            user.save()
            
            return Response({
                'message': 'Onboarding complete. You now have full access.',
                'user_details': {
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'phone_number': user.phone_number,
                    'address': user.address,
                    'email': user.email
                }
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Forgot Password
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
                
                if user.otp_created_at:
                    expiry_time = user.otp_created_at + timedelta(minutes=2)
                    if timezone.now() > expiry_time:
                        return Response({'error': 'OTP has expired'}, status=status.HTTP_400_BAD_REQUEST)

                user.set_password(new_password)
                user.otp = None
                user.otp_created_at = None
                user.save()
                return Response({'message': 'Password reset successful'}, status=status.HTTP_200_OK)
            except User.DoesNotExist:
                return Response({'error': 'Invalid OTP or Email'}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# --- Booking APIs (Gated by Onboarding) ---

class HotelListView(views.APIView):
    permission_classes = [permissions.IsAuthenticated, IsOnboardingCompletedPermission]

    @extend_schema(request=HotelListSerializer, responses={201: dict})
    def post(self, request):
        serializer = HotelListSerializer(data=request.data)
        if serializer.is_valid():
            instance = serializer.save(user=request.user)
            
            # --- Email Notification ---
            subject = 'Hotel Search Confirmation'
            message = f"Hello {instance.customer_name},\n\nYour hotel search at {instance.place} has been saved.\nCheck-in: {instance.checkin_date}\nCheck-out: {instance.checkout_date}\n\nCoupon Code: {instance.coupon}\n\nThank you for choosing CheapTicket!"
            
            try:
                send_mail(
                    subject,
                    message,
                    settings.EMAIL_HOST_USER,
                    ['support@cheaptickethub.com'],
                    fail_silently=True,
                )
            except Exception:
                pass

            response_serializer = HotelListSerializer(instance)
            return Response({'message': 'Hotel search saved successfully', 'data': response_serializer.data}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class FlightListView(views.APIView):
    permission_classes = [permissions.IsAuthenticated, IsOnboardingCompletedPermission]

    @extend_schema(request=FlightListSerializer, responses={201: dict})
    def post(self, request):
        serializer = FlightListSerializer(data=request.data)
        if serializer.is_valid():
            instance = serializer.save(user=request.user)
            
            # --- Email Notification ---
            subject = 'Flight Search Confirmation'
            trip_type = "Round Trip" if instance.round_trip else "One Way"
            message = f"Hello {instance.customer_name},\n\nYour flight search has been saved.\n\nFlight Details:\n{instance.from_location} to {instance.to_location}\nDeparture: {instance.departure_date}\nType: {trip_type}\n\nCoupon Code: {instance.coupon}\n\nThank you for choosing CheapTicket!"
            
            try:
                send_mail(
                    subject,
                    message,
                    settings.EMAIL_HOST_USER,
                    ['support@cheaptickethub.com'],
                    fail_silently=True,
                )
            except Exception:
                pass

            response_serializer = FlightListSerializer(instance)
            return Response({'message': 'Flight search saved successfully', 'data': response_serializer.data}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RentalCarListView(views.APIView):
    permission_classes = [permissions.IsAuthenticated, IsOnboardingCompletedPermission]

    @extend_schema(request=RentalCarListSerializer, responses={201: dict})
    def post(self, request):
        serializer = RentalCarListSerializer(data=request.data)
        if serializer.is_valid():
            instance = serializer.save(user=request.user)
            
            # --- Email Notification ---
            subject = 'Rental Car Search Confirmation'
            message = f"Hello {instance.customer_name},\n\nYour rental car search at {instance.location} has been saved.\nPickup: {instance.pickup_time}\nDrop-off: {instance.dropoff_time}\n\nCoupon Code: {instance.coupon}\n\nThank you for choosing CheapTicket!"
            
            try:
                send_mail(
                    subject,
                    message,
                    settings.EMAIL_HOST_USER,
                    ['support@cheaptickethub.com'],
                    fail_silently=True,
                )
            except Exception:
                pass

            response_serializer = RentalCarListSerializer(instance)
            return Response({'message': 'Rental Car search saved successfully', 'data': response_serializer.data}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class HolidayPackageListView(views.APIView):
    permission_classes = [permissions.IsAuthenticated, IsOnboardingCompletedPermission]

    @extend_schema(request=HolidayPackageListSerializer, responses={201: dict})
    def post(self, request):
        serializer = HolidayPackageListSerializer(data=request.data)
        if serializer.is_valid():
            instance = serializer.save(user=request.user)
            
            # --- Email Notification ---
            subject = 'Holiday Package Search Confirmation'
            message = f"Hello {instance.customer_name},\n\nYour holiday package search for {instance.to_location} has been saved.\nDuration: {instance.duration} days\n\nCoupon Code: {instance.coupon}\n\nThank you for choosing CheapTicket!"
            
            try:
                send_mail(
                    subject,
                    message,
                    settings.EMAIL_HOST_USER,
                    ['support@cheaptickethub.com'],
                    fail_silently=True,
                )
            except Exception:
                pass

            response_serializer = HolidayPackageListSerializer(instance)
            return Response({'message': 'Holiday Package search saved successfully', 'data': response_serializer.data}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CruiseListView(views.APIView):
    permission_classes = [permissions.IsAuthenticated, IsOnboardingCompletedPermission]

    @extend_schema(request=CruiseListSerializer, responses={201: dict})
    def post(self, request):
        serializer = CruiseListSerializer(data=request.data)
        if serializer.is_valid():
            instance = serializer.save(user=request.user)
            
            # --- Email Notification ---
            subject = 'Cruise Search Confirmation'
            message = f"Hello {instance.customer_name},\n\nYour cruise search for {instance.to_location} has been saved.\nDuration: {instance.duration} days\nCabins: {instance.cabins}\n\nCoupon Code: {instance.coupon}\n\nThank you for choosing CheapTicket!"
            
            try:
                send_mail(
                    subject,
                    message,
                    settings.EMAIL_HOST_USER,
                    ['support@cheaptickethub.com'],
                    fail_silently=True,
                )
            except Exception:
                pass

            response_serializer = CruiseListSerializer(instance)
            return Response({'message': 'Cruise search saved successfully', 'data': response_serializer.data}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class MultiCityFlightListView(views.APIView):
    permission_classes = [permissions.IsAuthenticated, IsOnboardingCompletedPermission]

    @extend_schema(request=MultiCityFlightSerializer, responses={201: dict})
    def post(self, request):
        serializer = MultiCityFlightSerializer(data=request.data)
        if serializer.is_valid():
            # Save the multi-city flight and its legs
            instance = serializer.save(user=request.user)
            
            # --- Email Notification (Like Nodemailer in Node.js) ---
            # We can use Django's send_mail function
            subject = 'Multi-City Flight Search Confirmation'
            legs_info = "\n".join([f"- {leg.from_location} to {leg.to_location} on {leg.departure_date}" for leg in instance.legs.all()])
            message = f"Hello {instance.customer_name},\n\nYour multi-city flight search has been saved.\n\nFlight Details:\n{legs_info}\n\nCoupon Code: {instance.coupon}\n\nThank you for choosing CheapTicket!"
            
            try:
                send_mail(
                    subject,
                    message,
                    settings.EMAIL_HOST_USER,
                    ['support@cheaptickethub.com'],
                    fail_silently=True,
                )
            except Exception as e:
                # Log error or handle it (optional)
                pass

            response_serializer = MultiCityFlightSerializer(instance)
            return Response({'message': 'Multi-city flight search saved successfully', 'data': response_serializer.data}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ContactSupportView(views.APIView):
    permission_classes = [permissions.AllowAny]

    @extend_schema(request=ContactSupportSerializer, responses={200: dict})
    def post(self, request):
        serializer = ContactSupportSerializer(data=request.data)
        if serializer.is_valid():
            name = serializer.validated_data['name']
            email = serializer.validated_data['email']
            subject = serializer.validated_data['subject']
            message = serializer.validated_data['message']

            full_message = f"Name: {name}\nEmail: {email}\n\nMessage:\n{message}"
            
            try:
                send_mail(
                    subject,
                    full_message,
                    settings.EMAIL_HOST_USER,
                    ['support@cheaptickethub.com'],
                    fail_silently=False,
                )
                return Response({'message': 'Your message has been sent successfully.'}, status=status.HTTP_200_OK)
            except Exception as e:
                return Response({'error': 'Failed to send message. Please try again later.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
