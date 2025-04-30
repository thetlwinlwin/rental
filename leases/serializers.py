from properties.models import Property
from rest_framework import serializers
from users.serializers import SimpleUserSerializer, UserSerializer

from .models import Lease, Review


class SimplePropertySerializer(serializers.ModelSerializer):
    class Meta:
        model = Property
        fields = ['id', 'title', 'address_line_1', 'township',] 
        depth = 1 

class LeaseSerializer(serializers.ModelSerializer): 
    property_details = SimplePropertySerializer(source='property', read_only=True) 
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    property = serializers.PrimaryKeyRelatedField(
        queryset=Property.objects.all(), 
        write_only=True 
    )
    counterparty_details = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = Lease
        fields = [
            'id',
            'property', 
            'property_details', 
            'tenant', 
            'counterparty_details',
            'start_date',
            'end_date',
            'status', 
            'status_display', 
            'monthly_rent_at_signing', 
            'deposit_paid_amount',
            'deposit_paid_date',
            'lease_document', 
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'id', 'tenant', 'status', 'created_at', 'updated_at',
            'property_details', 'counterparty_details', 'status_display',
            'monthly_rent_at_signing'
        ]
    def get_counterparty_details(self, obj): 
        request = self.context.get('request')
        if not request or not hasattr(request, 'user') or not request.user.is_authenticated:
            return None
        current_user = request.user
        lease = obj 
        if not lease.tenant or not lease.property or not lease.property.owner:
             return None 
        if current_user == lease.tenant:
            serializer = SimpleUserSerializer(lease.property.owner, context=self.context)
            return serializer.data
        elif current_user == lease.property.owner:
            serializer = SimpleUserSerializer(lease.tenant, context=self.context)
            return serializer.data
        else:
            return None


    
    
    
    
    
    
    
    
    
    


class ReviewSerializer(serializers.ModelSerializer):
    
    
    reviewer_details = UserSerializer(source='reviewer', read_only=True)
    
    lease_info = serializers.SerializerMethodField(read_only=True)

    
    
    

    class Meta:
        model = Review
        fields = [
            'id',
            'lease', 
            'lease_info', 
            'reviewer', 
            'reviewer_details', 
            'rating',
            'comment',
            'created_at',
        ]
        read_only_fields = [
            'id', 'lease', 'reviewer', 'created_at',
            'reviewer_details', 'lease_info'
        ]

    def get_lease_info(self, obj):
        
        if obj.lease:
            return {
                'id': obj.lease.id,
                'property_title': obj.lease.property.title,
                'start_date': obj.lease.start_date,
                'end_date': obj.lease.end_date,
            }
        return None

    def validate(self, data):
        """
        Add validation specific to creating/updating Reviews.
        Assumes 'lease' and 'reviewer' instances are added to serializer context
        by the view before validation.
        """
        lease = self.context.get('lease')
        request = self.context.get('request')
        reviewer = request.user if request else None

        if not lease:
             
             raise serializers.ValidationError("Lease context is missing.")
        if not reviewer:
             raise serializers.ValidationError("Request context (reviewer) is missing.")

        
        if lease.tenant != reviewer:
            raise serializers.ValidationError("You can only review leases for which you were the tenant.")

        
        if lease.status != Lease.LeaseStatus.COMPLETED:
            raise serializers.ValidationError("You can only review completed leases.")

        
        
        
        is_update = self.instance is not None
        if not is_update and Review.objects.filter(lease=lease).exists():
             raise serializers.ValidationError("A review for this lease already exists.")

        
        rating = data.get('rating')
        if rating is not None and not (1 <= rating <= 5):
             raise serializers.ValidationError("Rating must be between 1 and 5.")

        return data

    def create(self, validated_data):
        
        lease = self.context.get('lease')
        reviewer = self.context.get('request').user
        validated_data['lease'] = lease
        validated_data['reviewer'] = reviewer
        return super().create(validated_data)