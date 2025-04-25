import decimal

from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from django.db import models
from django.utils.text import slugify


class PropertyType(models.Model):
    name = models.CharField(max_length=100, unique=True, help_text="Type of the property (e.g., Apartment, House)")
    slug = models.SlugField(max_length=110, unique=True, blank=True, help_text="URL-friendly version of the name, auto-generated if blank.")
    description = models.TextField(blank=True, null=True, help_text="Optional description of the property type.")

    class Meta:
        verbose_name = "Property Type"
        verbose_name_plural = "Property Types"
        ordering = ['name']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

class Amenity(models.Model):
    name = models.CharField(max_length=100, unique=True, help_text="Name of the amenity (e.g., Air Conditioning, Parking)")
    slug = models.SlugField(max_length=110, unique=True, blank=True, help_text="URL-friendly version of the name.")

    class Meta:
        verbose_name = "Amenity"
        verbose_name_plural = "Amenities"
        ordering = ['name']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Property(models.Model):
    class AvailabilityStatus(models.TextChoices):
        AVAILABLE = 'AV', 'Available'
        RENTED = 'RE', 'Rented'
        PENDING = 'PE', 'Pending Lease'
        UNAVAILABLE = 'UN', 'Unavailable'

    class PetPolicy(models.TextChoices):
        NO_PETS = 'NO', 'No Pets Allowed'
        CATS_ONLY = 'CA', 'Cats Only'
        DOGS_ONLY = 'DO', 'Dogs Only'
        ALLOWED = 'AL', 'Pets Allowed'
        CASE_BY_CASE = 'CB', 'Case by Case'

    class ParkingType(models.TextChoices):
        NONE = 'NO', 'No Parking'
        STREET = 'ST', 'Street Parking'
        DRIVEWAY = 'DR', 'Driveway'
        GARAGE = 'GA', 'Garage'
        ASSIGNED = 'AS', 'Assigned Spot'

    title = models.CharField(max_length=250, help_text="Catchy title for the property listing.")
    description = models.TextField(help_text="Detailed description of the property.")
    property_type = models.ForeignKey(
        PropertyType,
        related_name='properties',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="The type of property."
    )
    owner = models.ForeignKey(
        User, # Landlord/Owner using Django's User model
        related_name='properties_owned',
        on_delete=models.CASCADE, # Consider PROTECT if needed
        help_text="The user (Landlord) who owns this property."
    )


    address_line_1 = models.CharField(max_length=255, help_text="Street address, building name/number, floor, etc.")
    address_line_2 = models.CharField(max_length=255, blank=True, null=True, help_text="Additional address details (Optional)")
    township = models.ForeignKey(
        'locations.Township',
        related_name='properties',
        on_delete=models.PROTECT,   
        help_text="The specific Township where the property is located (Yangon/Mandalay)."
    )
    latitude = models.DecimalField(max_digits=10, decimal_places=7, blank=True, help_text="Optional Latitude for mapping.")
    longitude = models.DecimalField(max_digits=10, decimal_places=7, blank=True, help_text="Optional Longitude for mapping.")


    price_per_month = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(decimal.Decimal('0.01'))],
        help_text="Rental price per month (e.g., in MMK)."
    )
    deposit_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0.00,
        validators=[MinValueValidator(decimal.Decimal('0.00'))],
        help_text="Security deposit amount."
    )


    bedrooms = models.PositiveIntegerField(default=1, help_text="Number of bedrooms.")
    bathrooms = models.DecimalField(max_digits=3, decimal_places=1, default=1.0, help_text="Number of bathrooms (e.g., 1.0, 1.5, 2.0).")
    area_sqft = models.PositiveIntegerField(blank=True, null=True, help_text="Area in square feet.") # Or use area_sqm
    is_furnished = models.BooleanField(default=False, help_text="Is the property furnished?")
    pet_policy = models.CharField(max_length=2, choices=PetPolicy.choices, default=PetPolicy.NO_PETS)
    parking_type = models.CharField(max_length=2, choices=ParkingType.choices, default=ParkingType.NONE)
    amenities = models.ManyToManyField(
        Amenity,
        blank=True,
        related_name='properties',
        help_text="Select available amenities."
    )

    availability_status = models.CharField(
        max_length=2,
        choices=AvailabilityStatus.choices,
        default=AvailabilityStatus.AVAILABLE,
        help_text="Current availability status."
    )
    available_from_date = models.DateField(blank=True, null=True, help_text="Date the property becomes available for move-in.")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Property"
        verbose_name_plural = "Properties"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} ({self.township.name}, {self.township.city_district.name})"

    @property
    def city_district(self):
        return self.township.city_district

    @property
    def region_state(self):
        return self.township.city_district.region_state


class PropertyImage(models.Model):
    property = models.ForeignKey(
        Property,
        related_name='images',
        on_delete=models.CASCADE,
        help_text="The property this image belongs to."
    )
    image = models.ImageField(
        upload_to='property_images/', 
        help_text="Image file."
    )
    order = models.PositiveIntegerField(default=0)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Property Image"
        verbose_name_plural = "Property Images"
        ordering = ['order',]

    def __str__(self):
        return f"Image for {self.property.title}"