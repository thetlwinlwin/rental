from locations.models import Township
from locations.serializers import TownshipSerializer
from rest_framework import serializers

from .models import Amenity, Property, PropertyImage, PropertyType


class BulkPropertyImageSerializer(serializers.Serializer):
    images = serializers.ListField(
        child=serializers.ImageField(max_length=100000, allow_empty_file=False),
        write_only=True
    )

    def validate(self, data):
        images = data.get('images', [])   
        if len(images) > 10:
            raise serializers.ValidationError("Maximum 10 images allowed per upload")     
        return data

    def create(self, validated_data):
        property = self.context['property']
        images = validated_data.get('images', [])
        created_images = []
        for image in images:
            img = PropertyImage.objects.create(
                property=property,
                image=image,
    
            )
            created_images.append(img)      
        return created_images

    def to_representation(self, instance):  
        return PropertyImageSerializer(instance, many=True).data


class PropertyImageSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()
    
    class Meta:
        model = PropertyImage
        fields = ['id', 'image_url']
        read_only_fields = fields

    def get_image_url(self, obj):
        request = self.context.get('request')
        if obj.image and request:
            return request.build_absolute_uri(obj.image.url)
        return None

class AmenitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Amenity
        fields = ['id', 'name', 'slug']

class PropertyTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = PropertyType
        fields = ['id', 'name', 'slug']


class PropertySerializer(serializers.ModelSerializer):
    
    owner_username = serializers.CharField(source='owner.username', read_only=True)
    owner_phone = serializers.CharField(source='owner.profile.phone_number', read_only=True, allow_null=True)
    owner_is_verified = serializers.BooleanField(source='owner.profile.is_verified_landlord', read_only=True)
    property_type = PropertyTypeSerializer(read_only=True)
    township = TownshipSerializer(read_only=True)
    amenities = AmenitySerializer(many=True, read_only=True)
    images = PropertyImageSerializer(many=True, read_only=True) 
    latitude = serializers.DecimalField(
        max_digits=10,
        decimal_places=7,
        required=True,
        allow_null=False  
    )
    longitude = serializers.DecimalField(
        max_digits=10,
        decimal_places=7,
        required=True,
        allow_null=False  
    )
    
    
    property_type_id = serializers.PrimaryKeyRelatedField(
        queryset=PropertyType.objects.all(), source='property_type', write_only=True, required=False, allow_null=True)
    township_id = serializers.PrimaryKeyRelatedField(
        queryset=Township.objects.all(), source='township', write_only=True)
    amenity_ids = serializers.PrimaryKeyRelatedField(
        queryset=Amenity.objects.all(), source='amenities', write_only=True, many=True, required=False)

    class Meta:
        model = Property
        fields = [
            'id', 'title', 'description',
            'owner', 'owner_username', 
            'property_type', 'property_type_id', 
            'address_line_1', 'address_line_2',
            'township', 'township_id', 
            'latitude', 'longitude',
            'price_per_month', 'deposit_amount',
            'bedrooms', 'bathrooms', 'area_sqft', 'is_furnished',
            'pet_policy', 'parking_type',
            'amenities', 'amenity_ids', 
            'availability_status', 'available_from_date',
            'images', 
            'created_at', 'updated_at','owner_username',
            'owner_phone', 
            'owner_is_verified',
        ]
        
        read_only_fields = ['owner', 'created_at', 'updated_at']