from dj_rest_auth.registration.serializers import RegisterSerializer
from django.contrib.auth.models import User
from rest_framework import serializers

from .models import Profile


class ProfileSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    profile_picture = serializers.ImageField(max_length=None, use_url=True, required=False, allow_null=True)
    class Meta:
        model = Profile
        fields = [
            'id', 'user', 'role', 'phone_number', 'address',
            'bio', 'profile_picture', 'is_verified_landlord',
            'updated_at'
        ]
        read_only_fields = ['user', 'is_verified_landlord']

class SimpleProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = [
            'phone_number','role','address'
        ]
        read_only_fields = ['user', 'is_verified_landlord']

class SimpleUserSerializer(serializers.ModelSerializer):
    profile = SimpleProfileSerializer(read_only=True)
    class Meta:
        model = User
        fields = [ 'username','first_name','last_name','profile' ] 
        depth = 1 

class UserSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer(read_only=True)

    class Meta:
        model = User 
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'profile', 
            'is_active', 'date_joined'
        ]
        read_only_fields = ['is_active', 'date_joined', 'profile']


class CurrentUserProfileUpdateSerializer(serializers.ModelSerializer):
    profile_picture = serializers.ImageField(max_length=None, use_url=True, required=False, allow_null=True)

    class Meta:
        model = Profile
        fields = ['phone_number', 'address', 'bio', 'profile_picture']


class CustomRegisterSerializer(RegisterSerializer):
    first_name = serializers.CharField(max_length=30, required=True)
    last_name = serializers.CharField(max_length=30, required=True)
    role = serializers.ChoiceField(choices=Profile.Role.choices, required=True)

    def get_cleaned_data(self):
        data = super().get_cleaned_data()
        data['first_name'] = self.validated_data.get('first_name', '')
        data['last_name'] = self.validated_data.get('last_name', '')
        data['role'] = self.validated_data.get('role', Profile.Role.TENANT)
        return data

    def custom_signup(self, request, user):
        role = self.validated_data.get('role', Profile.Role.TENANT) 
        profile = user.profile
        profile.role = role
        profile.save()