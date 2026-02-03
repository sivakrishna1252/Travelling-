from django.urls import path
from .views import (
    SendOTPView, VerifyOTPView, CompleteOnboardingView, ForgotPasswordView,
    HotelListView, FlightListView, RentalCarListView, HolidayPackageListView, CruiseListView
)


urlpatterns = [
    path('send-otp/', SendOTPView.as_view(), name='send-otp'),
    path('verify-otp/', VerifyOTPView.as_view(), name='verify-otp'),
    path('onboarding/', CompleteOnboardingView.as_view(), name='onboarding'),
    path('forgot-password/', ForgotPasswordView.as_view(), name='forgot-password'),
    # path('complete-onboarding/', CompleteOnboardingView.as_view(), name='complete-onboarding'),
    path('hotel/', HotelListView.as_view(), name='hotel'),
    path('flight/', FlightListView.as_view(), name='flight'),
    path('rentalcar/', RentalCarListView.as_view(), name='rentalcar'),
    path('holidaypackage/', HolidayPackageListView.as_view(), name='holidaypackage'),
    path('cruise/', CruiseListView.as_view(), name='cruise'),
]

