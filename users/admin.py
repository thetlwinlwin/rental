from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User

from .models import Profile


class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False 
    verbose_name_plural = 'Profile'
    fk_name = 'user'
    fields = ('role', 'phone_number', 'address', 'bio', 'profile_picture', 'is_verified_landlord') 


class UserAdmin(BaseUserAdmin):
    inlines = (ProfileInline,)
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'get_role', 'is_verified_landlord_status') 
    list_select_related = ('profile',) 

    
    @admin.display(description='Role')
    def get_role(self, instance):
        if hasattr(instance, 'profile'):
            return instance.profile.get_role_display()
        return None

    
    @admin.display(description='Landlord Verified', boolean=True)
    def is_verified_landlord_status(self, instance):
         if hasattr(instance, 'profile'):
            return instance.profile.is_verified_landlord
         return False


admin.site.unregister(User) 
admin.site.register(User, UserAdmin) 


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'role', 'phone_number', 'is_verified_landlord', 'updated_at')
    list_filter = ('role', 'is_verified_landlord')
    search_fields = ('user__username', 'phone_number')