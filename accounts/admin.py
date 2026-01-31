from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Customer, Hotel, Flight, RentalCar, HolidayPackage, Cruise
class CustomUserAdmin(UserAdmin):
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
class CustomerAdmin(admin.ModelAdmin):
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
class HotelAdmin(admin.ModelAdmin):
    list_display = ('display_name', 'user_email', 'place', 'date', 'adults', 'children', 'rooms', 'coupon')
    list_filter = ('place', 'date', 'user')
    search_fields = ('place', 'user__email', 'user__first_name', 'user__last_name')

    fieldsets = (
        ('Hotel Details', {
            'fields': ('user', 'place', 'date', 'adults', 'children', 'rooms', 'coupon')
        }),
    )

    def user_email(self, obj):
        return obj.user.email if obj.user else "Anonymous"
    user_email.short_description = 'User Email'



#flight
@admin.register(Flight)
class FlightAdmin(admin.ModelAdmin):
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
class RentalCarAdmin(admin.ModelAdmin):
    list_display = ('display_name', 'user_email', 'location', 'pickup_time', 'dropoff_time', 'adults', 'children', 'coupon')
    list_filter = ('location', 'pickup_time', 'dropoff_time', 'user')
    search_fields = ('location', 'user__email', 'user__first_name', 'user__last_name')

    fieldsets = (
        ('Rental Car Details', {
            'fields': ('user', 'location', 'pickup_time', 'dropoff_time', 'adults', 'children', 'coupon')
        }),
    )

    def user_email(self, obj):
        return obj.user.email if obj.user else "Anonymous"
    user_email.short_description = 'User Email'


#holiday packages
@admin.register(HolidayPackage)
class HolidayPackageAdmin(admin.ModelAdmin):
    list_display = ('display_name', 'user_email', 'to_location', 'from_location', 'duration', 'passengers', 'coupon')
    list_filter = ('to_location', 'from_location', 'duration', 'user')
    search_fields = ('to_location', 'from_location', 'user__email', 'user__first_name', 'user__last_name')

    fieldsets = (
        ('Holiday Package Details', {
            'fields': ('user', 'to_location', 'from_location', 'duration', 'passengers', 'coupon')
        }),
    )

    def user_email(self, obj):
        return obj.user.email if obj.user else "Anonymous"
    user_email.short_description = 'User Email'


#cruise
@admin.register(Cruise)
class CruiseAdmin(admin.ModelAdmin):
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
