from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import Group
from unfold.admin import ModelAdmin
from unfold.forms import AdminPasswordChangeForm, UserChangeForm, UserCreationForm

from .models import User, Customer, Hotel, Flight, RentalCar, HolidayPackage, Cruise

# Unregister default Group admin to optionaly use the Unfold one if needed, 
# but usually we just want to ensure our UserAdmin uses Unfold.
admin.site.unregister(Group)
from django.contrib.auth.admin import GroupAdmin as BaseGroupAdmin
@admin.register(Group)
class GroupAdmin(BaseGroupAdmin, ModelAdmin):
    pass


class CustomUserAdmin(BaseUserAdmin, ModelAdmin):
    form = UserChangeForm
    add_form = UserCreationForm
    change_password_form = AdminPasswordChangeForm
    
    model = User
    list_display = ('email', 'first_name', 'last_name', 'phone_number', 'is_staff', 'is_active')
    list_filter = ('is_staff', 'is_active')
    ordering = ('email',)
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal Info', {'fields': ('first_name', 'last_name', 'phone_number', 'address')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser')}),
    )

@admin.register(Customer)
class CustomerAdmin(ModelAdmin):
    def get_queryset(self, request):
        return super().get_queryset(request).filter(is_staff=False)

    list_display = ('email', 'first_name', 'last_name', 'phone_number', 'is_onboarding_completed')
    list_filter = ('is_onboarding_completed', 'is_auth_required')
    search_fields = ('email', 'first_name', 'last_name', 'phone_number')

    fieldsets = (
        ('Customer Info', {'fields': ('email', 'first_name', 'last_name', 'phone_number', 'address')}),
        ('Status', {'fields': ('is_onboarding_completed', 'is_auth_required')}),
    )

admin.site.register(User, CustomUserAdmin)


#hotel
@admin.register(Hotel)
class HotelAdmin(ModelAdmin):
    list_display = ('display_name', 'user_email', 'place', 'checkin_date', 'checkout_date', 'adults', 'children', 'rooms', 'coupon')
    list_filter = ('place', 'checkin_date', 'checkout_date', 'user')
    search_fields = ('place', 'user__email', 'user__first_name', 'user__last_name')

    fieldsets = (
        ('Hotel Details', {
            'fields': ('user', 'place', 'checkin_date', 'checkout_date', 'adults', 'children', 'rooms', 'coupon')
        }),
    )

    def user_email(self, obj):
        return obj.user.email if obj.user else "Anonymous"
    user_email.short_description = 'User Email'



#flight
@admin.register(Flight)
class FlightAdmin(ModelAdmin):
    list_display = ('display_name', 'user_email', 'from_location', 'to_location', 'round_trip', 'one_way', 'departure_date', 'return_date', 'adults', 'children', 'coupon')
    list_filter = ('from_location', 'to_location', 'round_trip', 'one_way', 'departure_date', 'return_date', 'user')
    search_fields = ('from_location', 'to_location', 'user__email', 'user__first_name', 'user__last_name')

    fieldsets = (
        ('Flight Details', {
            'fields': ('user', 'from_location', 'to_location', 'round_trip', 'one_way', 'departure_date', 'return_date', 'adults', 'children', 'coupon')
        }),
    )

    def user_email(self, obj):
        return obj.user.email if obj.user else "Anonymous"
    user_email.short_description = 'User Email'


#rental car
@admin.register(RentalCar)
class RentalCarAdmin(ModelAdmin):
    list_display = ('display_name', 'user_email', 'location', 'pickup_time', 'dropoff_time', 'coupon')
    list_filter = ('location', 'pickup_time', 'dropoff_time', 'user')
    search_fields = ('location', 'user__email', 'user__first_name', 'user__last_name')

    fieldsets = (
        ('Rental Car Details', {
            'fields': ('user', 'location', 'pickup_time', 'dropoff_time', 'coupon')
        }),
    )

    def user_email(self, obj):
        return obj.user.email if obj.user else "Anonymous"
    user_email.short_description = 'User Email'


#holiday packages
@admin.register(HolidayPackage)
class HolidayPackageAdmin(ModelAdmin):
    list_display = ('display_name', 'user_email', 'to_location', 'from_location', 'duration', 'adults', 'children', 'coupon')
    list_filter = ('to_location', 'from_location', 'duration', 'user')
    search_fields = ('to_location', 'from_location', 'user__email', 'user__first_name', 'user__last_name')

    fieldsets = (
        ('Holiday Package Details', {
            'fields': ('user', 'to_location', 'from_location', 'duration', 'adults', 'children', 'coupon')
        }),
    )

    def user_email(self, obj):
        return obj.user.email if obj.user else "Anonymous"
    user_email.short_description = 'User Email'


#cruise
@admin.register(Cruise)
class CruiseAdmin(ModelAdmin):
    list_display = ('display_name', 'user_email', 'to_location', 'from_location', 'duration', 'cabins', 'adults', 'children', 'coupon')
    list_filter = ('to_location', 'from_location', 'duration', 'user')
    search_fields = ('to_location', 'from_location', 'user__email', 'user__first_name', 'user__last_name')

    fieldsets = (
        ('Cruise Details', {
            'fields': ('user', 'to_location', 'from_location', 'duration', 'cabins', 'adults', 'children', 'coupon')
        }),
    )

    def user_email(self, obj):
        return obj.user.email if obj.user else "Anonymous"
    user_email.short_description = 'User Email'


