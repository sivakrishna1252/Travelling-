from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import Group
from django.utils.html import format_html
from django import forms
from unfold.admin import ModelAdmin
from unfold.decorators import display
from unfold.forms import AdminPasswordChangeForm, UserChangeForm, UserCreationForm
from unfold.widgets import UnfoldAdminTextInputWidget, UnfoldAdminEmailInputWidget, UnfoldAdminTextareaWidget

from .models import User, Customer, Hotel, Flight, RentalCar, HolidayPackage, Cruise, AuthUser, OTPLog

# --- Custom Forms ---

class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = AuthUser
        fields = ("email",)

class CustomUserChangeForm(UserChangeForm):
    class Meta(UserChangeForm.Meta):
        model = AuthUser
        fields = ("email",)

class CustomerCreationForm(forms.ModelForm):
    """
    Special form for adding a customer directly with full profile details.
    Removed password field and added explicit Unfold widgets for better styling.
    """
    class Meta:
        model = Customer
        fields = (
            'email', 'first_name', 'last_name', 'phone_number', 
            'address', 'is_onboarding_completed', 'is_active'
        )
        widgets = {
            'email': UnfoldAdminEmailInputWidget,
            'first_name': UnfoldAdminTextInputWidget,
            'last_name': UnfoldAdminTextInputWidget,
            'phone_number': UnfoldAdminTextInputWidget,
            'address': UnfoldAdminTextareaWidget(attrs={'rows': 3}),
        }

    def save(self, commit=True):
        user = super().save(commit=False)
        # Automatically set unusable password since it's an OTP-based signup flow
        user.set_unusable_password()
        user.is_staff = False
        if commit:
            user.save()
        return user

# --- Admin Classes ---

if admin.site.is_registered(Group):
    admin.site.unregister(Group)

@admin.register(Group)
class GroupAdmin(ModelAdmin):
    pass

class CustomUserAdmin(BaseUserAdmin, ModelAdmin):
    form = CustomUserChangeForm
    add_form = CustomUserCreationForm
    change_password_form = AdminPasswordChangeForm
    
    model = AuthUser
    list_display = ('display_user_profile', 'email', 'phone_number', 'otp', 'is_onboarding_completed', 'display_status_active', 'display_status_staff')
    list_filter = ('is_staff', 'is_active', 'is_onboarding_completed')
    ordering = ('email',)
    
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal Info', {'fields': ('first_name', 'last_name', 'phone_number', 'address')}),
        ('Auth Info', {'fields': ('otp', 'otp_created_at', 'is_onboarding_completed', 'is_email_verified')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password', 'is_active', 'is_staff', 'is_superuser'),
        }),
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
    add_form = CustomerCreationForm
    
    def get_form(self, request, obj=None, **kwargs):
        if obj is None:
            return self.add_form
        return super().get_form(request, obj, **kwargs)

    def get_queryset(self, request):
        return super().get_queryset(request).filter(is_staff=False)

    list_display = ('display_profile', 'phone_number', 'otp', 'display_onboarding', 'display_auth_required')
    list_filter = ('is_onboarding_completed', 'is_auth_required')
    search_fields = ('email', 'first_name', 'last_name', 'phone_number', 'otp')

    fieldsets = (
        (None, {'fields': ('email',)}),
        ('Onboarding Details', {'fields': ('first_name', 'last_name', 'phone_number', 'address', 'is_onboarding_completed')}),
        ('Permissions', {'fields': ('is_active', 'is_auth_required')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'first_name', 'last_name', 'phone_number', 'address', 'is_onboarding_completed', 'is_active'),
        }),
    )

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
    list_display = ('display_user_info', 'phone_number', 'place', 'checkin_date', 'display_guests', 'display_coupon')
    list_filter = ('place', 'checkin_date', 'user')
    search_fields = ('place', 'user__email', 'phone_number')
    fields = ('user', 'phone_number', 'place', 'checkin_date', 'checkout_date', 'adults', 'children', 'rooms', 'coupon')

    @display(description="Guests")
    def display_guests(self, obj):
        return f"{obj.adults} Adults, {obj.children} Kids"

@admin.register(Flight)
class FlightAdmin(ModelAdmin, TripDisplayMixin):
    list_display = ('display_user_info', 'phone_number', 'display_route', 'departure_date', 'display_type', 'display_coupon')
    list_filter = ('from_location', 'to_location', 'departure_date', 'round_trip')
    search_fields = ('from_location', 'to_location', 'user__email', 'phone_number')
    fields = ('user', 'phone_number', 'round_trip', 'one_way', 'from_location', 'to_location', 'departure_date', 'return_date', 'adults', 'children', 'coupon')
    
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
    list_display = ('display_user_info', 'phone_number', 'location', 'pickup_time', 'dropoff_time', 'display_coupon')
    list_filter = ('location', 'pickup_time', 'dropoff_time', 'user')
    search_fields = ('location', 'user__email', 'phone_number')
    fields = ('user', 'phone_number', 'location', 'pickup_time', 'dropoff_time', 'coupon')

@admin.register(HolidayPackage)
class HolidayPackageAdmin(ModelAdmin, TripDisplayMixin):
    list_display = ('display_user_info', 'phone_number', 'to_location', 'duration', 'display_coupon')
    list_filter = ('to_location', 'from_location', 'duration', 'user')
    search_fields = ('to_location', 'from_location', 'user__email', 'phone_number')
    fields = ('user', 'phone_number', 'from_location', 'to_location', 'duration', 'adults', 'children', 'coupon')

@admin.register(Cruise)
class CruiseAdmin(ModelAdmin, TripDisplayMixin):
    list_display = ('display_user_info', 'phone_number', 'to_location', 'duration', 'cabins', 'display_coupon')
    list_filter = ('to_location', 'from_location', 'duration', 'user')
    search_fields = ('to_location', 'from_location', 'user__email', 'phone_number')
    fields = ('user', 'phone_number', 'from_location', 'to_location', 'duration', 'cabins', 'adults', 'children', 'coupon')

@admin.register(OTPLog)
class OTPLogAdmin(ModelAdmin):
    list_display = ('display_user', 'phone_number', 'otp_code', 'timestamp', 'display_success')
    list_filter = ('is_successful', 'timestamp')
    search_fields = ('phone_number', 'otp_code', 'user__email')
    readonly_fields = ('timestamp',)

    @display(description="User")
    def display_user(self, obj):
        if obj.user:
            return obj.user.email
        return "Anonymous"

    @display(description="Status", label={
        True: "success",
        False: "danger"
    })
    def display_success(self, obj):
        return obj.is_successful