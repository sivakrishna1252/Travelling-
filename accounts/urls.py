from django.urls import path
from .views import (
    RegisterView, LoginView, LoginOTPView, SendOTPView, 
    VerifyOTPView, ForgotPasswordView, CompleteOnboardingView,
    HotelListView, FlightListView,RentalCarListView,HolidayPackageListView ,CruiseListView
)


urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('signin/', LoginView.as_view(), name='signin'),
    path('signin-otp/', LoginOTPView.as_view(), name='signin-otp'),
    path('send-otp-forgotpassword/', SendOTPView.as_view(), name='send-otp-forgotpassword'),
    path('verify-otp/', VerifyOTPView.as_view(), name='verify-otp'),
    path('forgot-password/', ForgotPasswordView.as_view(), name='forgot-password'),
    # path('complete-onboarding/', CompleteOnboardingView.as_view(), name='complete-onboarding'),
    path('hotel/', HotelListView.as_view(), name='hotel'),
    path('flight/', FlightListView.as_view(), name='flight'),
    path('rentalcar/', RentalCarListView.as_view(), name='rentalcar'),
    path('holidaypackage/', HolidayPackageListView.as_view(), name='holidaypackage'),
    path('cruise/', CruiseListView.as_view(), name='cruise'),
]

