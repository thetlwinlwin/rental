from django.conf import settings
from django.core.validators import RegexValidator
from django.db import models


class Profile(models.Model):
    class Role(models.TextChoices):
        TENANT = 'TE', 'Tenant'
        LANDLORD = 'LA', 'Landlord'
        BOTH = 'BO', 'Both' 

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='profile', 
        help_text="The user this profile belongs to."
    )
    role = models.CharField(
        max_length=2,
        choices=Role.choices,
        default=Role.TENANT, 
        help_text="User's primary role on the platform."
    )
    phone_regex = RegexValidator(regex=r'^\+?1?\d{9,15}$', message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.")
    phone_number = models.CharField(
        validators=[phone_regex],
        max_length=17,
        blank=True, 
        null=True,
        help_text="Contact phone number (e.g., +959xxxxxxxxx)."
    )
    address = models.TextField(
        blank=True,
        null=True,
        help_text="Contact address (distinct from property addresses)."
    )
    bio = models.TextField(
        blank=True,
        null=True,
        help_text="A short description about the user."
    )
    profile_picture = models.ImageField(
        upload_to='profile_pics/',
        blank=True,
        null=True,
        help_text="User's profile picture."
    )
    is_verified_landlord = models.BooleanField(
        default=False,
        help_text="Admin-verified status for landlords."
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "User Profile"
        verbose_name_plural = "User Profiles"

    def __str__(self):
        return f"{self.user.username}'s Profile ({self.get_role_display()})"
    

    