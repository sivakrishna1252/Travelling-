from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import Group
from django.utils.html import format_html
from django.urls import reverse
from unfold.admin import ModelAdmin
from unfold.decorators import display
from unfold.forms import AdminPasswordChangeForm, UserChangeForm, UserCreationForm

from .models import User, Customer, Hotel, Flight, RentalCar, HolidayPackage, Cruise, AuthUser

# Unregister default Group admin
admin.site.unregister(Group)

@admin.register(Group)
class GroupAdmin(ModelAdmin):
    pass


class CustomUserAdmin(BaseUserAdmin, ModelAdmin):
    form = UserChangeForm
    add_form = UserCreationForm
    change_password_form = AdminPasswordChangeForm
    
    model = User
    list_display = ('display_user_profile', 'email', 'phone_number', 'display_status_active', 'display_status_staff')
    list_filter = ('is_staff', 'is_active')
    ordering = ('email',)
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal Info', {'fields': ('first_name', 'last_name', 'phone_number', 'address')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser')}),
    )

    @display(description="User", header=True)
    def display_user_profile(self, obj):
        return [format_html(
            '<div class="flex items-center gap-3">'
            '<div class="w-10 h-10 rounded-full bg-gray-200 flex items-center justify-center text-gray-600 font-bold">{}</div>'
            '<div><div class="font-medium text-gray-900">{} {}</div><div class="text-xs text-gray-500">{}</div></div>'
            '</div>',
            obj.email[0].upper() if obj.email else "U",
            obj.first_name,
            obj.last_name,
            obj.email
        )]

    @display(description="Active Status", label=True)
    def display_status_active(self, obj):
        return obj.is_active

    @display(description="Staff Status", label=True)
    def display_status_staff(self, obj):
        return obj.is_staff


@admin.register(Customer)
class CustomerAdmin(ModelAdmin):
    def get_queryset(self, request):
        return super().get_queryset(request).filter(is_staff=False)

    list_display = ('display_profile', 'phone_number', 'display_onboarding', 'display_auth_required')
    list_filter = ('is_onboarding_completed', 'is_auth_required')
    search_fields = ('email', 'first_name', 'last_name', 'phone_number')

    @display(description="Customer", header=True)
    def display_profile(self, obj):
        initial = obj.first_name[0].upper() if obj.first_name else (obj.email[0].upper() if obj.email else "?")
        name = f"{obj.first_name} {obj.last_name}" if obj.first_name else "Unknown"
        return [format_html(
            '<div class="flex items-center gap-3">'
            '<div class="w-10 h-10 rounded-full bg-rose-100 flex items-center justify-center text-rose-600 font-bold">{}</div>'
            '<div><div class="font-medium text-gray-900">{}</div><div class="text-xs text-gray-500">{}</div></div>'
            '</div>',
            initial,
            name,
            obj.email
        )]

    @display(description="Onboarding", label={
        True: "success",
        False: "warning"
    })
    def display_onboarding(self, obj):
        return obj.is_onboarding_completed

    @display(description="Auth Required", label={
        True: "danger",
        False: "success"
    })
    def display_auth_required(self, obj):
        return obj.is_auth_required


admin.site.register(AuthUser, CustomUserAdmin)


# Mixin for common display methods
class TripDisplayMixin:
    @display(description="User", header=True)
    def display_user_info(self, obj):
        if not obj.user:
            return [format_html('<span class="text-gray-400">Anonymous</span>')]
        
        initial = obj.user.first_name[0].upper() if obj.user.first_name else (obj.user.email[0].upper() if obj.user.email else "?")
        name = f"{obj.user.first_name} {obj.user.last_name}" if obj.user.first_name else "Guest User"
        
        return [format_html(
            '<div class="flex items-center gap-3">'
            '<div class="w-8 h-8 rounded-full bg-blue-100 flex items-center justify-center text-blue-600 font-bold text-xs">{}</div>'
            '<div><div class="font-medium text-gray-900">{}</div><div class="text-xs text-gray-500">{}</div></div>'
            '</div>',
            initial,
            name,
            obj.user.email
        )]

    @display(description="Coupon", label=True)
    def display_coupon(self, obj):
        return obj.coupon


@admin.register(Hotel)
class HotelAdmin(ModelAdmin, TripDisplayMixin):
    list_display = ('display_user_info', 'place', 'checkin_date', 'display_guests', 'display_coupon')
    list_filter = ('place', 'checkin_date', 'user')
    search_fields = ('place', 'user__email')
    fields = ('user', 'place', 'checkin_date', 'checkout_date', 'adults', 'children', 'rooms', 'coupon')

    @display(description="Guests")
    def display_guests(self, obj):
        return f"{obj.adults} Adults, {obj.children} Kids"


@admin.register(Flight)
class FlightAdmin(ModelAdmin, TripDisplayMixin):
    list_display = ('display_user_info', 'display_route', 'departure_date', 'display_type', 'display_coupon')
    list_filter = ('from_location', 'to_location', 'departure_date', 'round_trip')
    fields = ('user', 'round_trip', 'one_way', 'from_location', 'to_location', 'departure_date', 'return_date', 'adults', 'children', 'coupon')
    
    @display(description="Route")
    def display_route(self, obj):
        return format_html(
            '<div class="flex items-center gap-2">'
            '<span class="font-medium">{}</span>'
            '<span class="text-gray-400">→</span>'
            '<span class="font-medium">{}</span>'
            '</div>',
            obj.from_location,
            obj.to_location
        )
    
    @display(description="Type", label={
        "Round Trip": "info", 
        "One Way": "warning"
    })
    def display_type(self, obj):
        return "Round Trip" if obj.round_trip else "One Way"


@admin.register(RentalCar)
class RentalCarAdmin(ModelAdmin, TripDisplayMixin):
    list_display = ('display_user_info', 'location', 'pickup_time', 'dropoff_time', 'display_coupon')
    list_filter = ('location', 'pickup_time', 'dropoff_time', 'user')
    search_fields = ('location', 'user__email')
    fields = ('user', 'location', 'pickup_time', 'dropoff_time', 'coupon')


@admin.register(HolidayPackage)
class HolidayPackageAdmin(ModelAdmin, TripDisplayMixin):
    list_display = ('display_user_info', 'to_location', 'duration', 'display_coupon')
    list_filter = ('to_location', 'from_location', 'duration', 'user')
    search_fields = ('to_location', 'from_location')
    fields = ('user', 'from_location', 'to_location', 'duration', 'adults', 'children', 'coupon')


@admin.register(Cruise)
class CruiseAdmin(ModelAdmin, TripDisplayMixin):
    list_display = ('display_user_info', 'to_location', 'duration', 'cabins', 'display_coupon')
    list_filter = ('to_location', 'from_location', 'duration', 'user')
    search_fields = ('to_location', 'from_location')
    fields = ('user', 'from_location', 'to_location', 'duration', 'cabins', 'adults', 'children', 'coupon')


