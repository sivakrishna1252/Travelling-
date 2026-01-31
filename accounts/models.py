from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager



class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)



class User(AbstractUser):   #customer table in db
    username = None
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    otp = models.CharField(max_length=6, blank=True, null=True)
    is_onboarding_completed = models.BooleanField(default=False)
    is_auth_required = models.BooleanField(default=True)
    is_email_verified = models.BooleanField(default=False)


    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()

    def __str__(self):
        if self.is_superuser:
            return "admin:apparatus"
        return self.first_name if self.first_name else self.email

class Customer(User):
    class Meta:
        proxy = True
        verbose_name = 'Customer'
        verbose_name_plural = 'Customers'

class AuthUser(User):
    class Meta:
        proxy = True
        app_label = 'auth'
        verbose_name = 'User'
        verbose_name_plural = 'Users'





#CRUD api's of HOTEL,FLIGTH,RENTALCARS,HOLIDAYPACKAGES,CRUISES


#hotel table in db
class Hotel(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='hotels', null=True, blank=True)
    place = models.CharField(max_length=255)
    checkin_date = models.DateField(null=True, blank=True)
    checkout_date = models.DateField(null=True, blank=True)
    adults = models.IntegerField(default=0)
    children = models.IntegerField(default=0)
    rooms = models.IntegerField(default=0)
    # phone_number = models.ForeignKey(User, on_delete=models.CASCADE, related_name='hotels', null=True, blank=True)
    coupon = models.CharField(max_length=50, blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.coupon or self.coupon.lower() == "string":
            from .models import Flight, RentalCar, HolidayPackage, Cruise
            total = Hotel.objects.count() + Flight.objects.count() + RentalCar.objects.count() + HolidayPackage.objects.count() + Cruise.objects.count()
            self.coupon = f"CTH0026{1201 + total}"
        super().save(*args, **kwargs)

    @property
    def display_name(self):
        if self.user and self.user.first_name:
            return self.user.first_name
        if self.user:
            return self.user.email
        return "Anonymous"

    def __str__(self):
        return f"Hotel Search at {self.place} by {self.display_name}"



#flight table in db

class Flight(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='flights', null=True, blank=True)
    round_trip = models.BooleanField(default=False)
    one_way = models.BooleanField(default=True)
    from_location = models.CharField(max_length=255)
    to_location = models.CharField(max_length=255)
    departure_date = models.DateField(null=True, blank=True)
    return_date = models.DateField(null=True, blank=True)
    adults = models.IntegerField(default=0)
    children = models.IntegerField(default=0)
    coupon = models.CharField(max_length=50, blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.coupon or self.coupon.lower() == "string":
            from .models import Hotel, RentalCar, HolidayPackage, Cruise
            total = Hotel.objects.count() + Flight.objects.count() + RentalCar.objects.count() + HolidayPackage.objects.count() + Cruise.objects.count()
            self.coupon = f"CTH0026{1201 + total}"
        super().save(*args, **kwargs)


    @property
    def display_name(self):
        if self.user and self.user.first_name:
            return self.user.first_name
        if self.user:
            return self.user.email
        return "Anonymous"

    def __str__(self):
        return f"Flight Search at {self.from_location} to {self.to_location} by {self.display_name}"



#rental cars table in db

class RentalCar(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='rental_cars', null=True, blank=True)
    location = models.CharField(max_length=255)
    pickup_time = models.DateTimeField(null=True, blank=True)
    dropoff_time = models.DateTimeField(null=True, blank=True)
    coupon = models.CharField(max_length=50, blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.coupon or self.coupon.lower() == "string":
            from .models import Hotel, Flight, HolidayPackage, Cruise
            total = Hotel.objects.count() + Flight.objects.count() + RentalCar.objects.count() + HolidayPackage.objects.count() + Cruise.objects.count()
            self.coupon = f"CTH0026{1201 + total}"
        super().save(*args, **kwargs)

    @property
    def display_name(self):
        if self.user and self.user.first_name:
            return self.user.first_name
        if self.user:
            return self.user.email
        return "Anonymous"

    def __str__(self):
        return f"Rental Car Search at {self.location} by {self.display_name} at {self.pickup_time} to {self.dropoff_time}"



#Holiday Packages table in db    
class HolidayPackage(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='holiday_packages', null=True, blank=True)
    to_location = models.CharField(max_length=255)
    from_location = models.CharField(max_length=255)
    duration = models.IntegerField()
    adults = models.IntegerField(default=0)
    children = models.IntegerField(default=0)
    coupon = models.CharField(max_length=50, blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.coupon or self.coupon.lower() == "string":
            from .models import Hotel, Flight, RentalCar, Cruise
            total = Hotel.objects.count() + Flight.objects.count() + RentalCar.objects.count() + HolidayPackage.objects.count() + Cruise.objects.count()
            self.coupon = f"CTH0026{1201 + total}"
        super().save(*args, **kwargs)

    @property
    def display_name(self):
        if self.user and self.user.first_name:
            return self.user.first_name
        if self.user:
            return self.user.email
        return "Anonymous"

    def __str__(self):
        return f"Holiday Package Search at {self.to_location} to {self.from_location} by {self.display_name} for {self.duration} days"


#CRUISES
class Cruise(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='cruises', null=True, blank=True)
    to_location = models.CharField(max_length=255)
    from_location = models.CharField(max_length=255)
    duration = models.IntegerField()
    cabins = models.CharField(max_length=255)
    adults = models.IntegerField(default=0)
    children = models.IntegerField(default=0)
    coupon = models.CharField(max_length=50, blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.coupon or self.coupon.lower() == "string":
            from .models import Hotel, Flight, RentalCar, HolidayPackage
            total = Hotel.objects.count() + Flight.objects.count() + RentalCar.objects.count() + HolidayPackage.objects.count() + Cruise.objects.count()
            self.coupon = f"CTH0026{1201 + total}"
        super().save(*args, **kwargs)

    @property
    def display_name(self):
        if self.user and self.user.first_name:
            return self.user.first_name
        if self.user:
            return self.user.email
        return "Anonymous"

    def __str__(self):
        return f"Cruise Search at {self.to_location} to {self.from_location} by {self.display_name} for {self.duration} days"        
