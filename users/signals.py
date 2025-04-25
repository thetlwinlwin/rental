from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token

from .models import Profile


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_user_profile(sender, instance, created, **kwargs):
    """
    Signal handler to create a Profile instance whenever a new User is created.
    """
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def save_user_profile(sender, instance, **kwargs):
    """
    Signal handler to save the profile whenever the User object is saved.
    (Useful if the profile needs updates based on User fields later)
    """
    if hasattr(instance, 'profile'):
        instance.profile.save()
    else:  
        Profile.objects.get_or_create(user=instance)


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    """
    Signal handler to create an Auth Token whenever a new User is created.
    """
    if created:
        Token.objects.create(user=instance)


