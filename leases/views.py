from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.utils import timezone
from properties.models import Property
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import NotFound, PermissionDenied, ValidationError
from rest_framework.response import Response

from .models import Lease, Review
from .permissions import IsPropertyOwner
from .serializers import LeaseSerializer, ReviewSerializer


class LeaseViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing Leases with explicit workflow.
    - Tenant POSTs to create (status=Pending).
    - Landlord uses /approve/ or /reject/ actions.
    - Updates are restricted after activation.
    """
    serializer_class = LeaseSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """ Users see leases where they are tenant or property owner. """
        user = self.request.user
        return Lease.objects.select_related(
            'property__owner', 'property__township', 'tenant__profile'
        ).filter(Q(tenant=user) | Q(property__owner=user))

    def perform_create(self, serializer):
        """ Tenant initiates lease request """
        property_instance = serializer.validated_data.get('property')
        start_date = serializer.validated_data.get('start_date')
        end_date = serializer.validated_data.get('end_date')

        if property_instance.owner == self.request.user:
            raise ValidationError("You cannot lease your own property.")

        if property_instance.availability_status != Property.AvailabilityStatus.AVAILABLE:
             raise ValidationError(f"Property '{property_instance.title}' is not currently available.")
        if start_date < timezone.now().date():
             raise ValidationError("Lease start date cannot be in the past.")


        rent_at_signing = property_instance.price_per_month
        serializer.save(
            tenant=self.request.user,
            status=Lease.LeaseStatus.PENDING,
            monthly_rent_at_signing=rent_at_signing
        )
    
    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.status != Lease.LeaseStatus.PENDING:
             return Response(
                 {"detail": "Updates not allowed for leases that are not Pending. Use specific actions."},
                 status=status.HTTP_403_FORBIDDEN
             ) 
        return Response({"detail": "Direct update disabled, use actions."}, status=status.HTTP_405_METHOD_NOT_ALLOWED)


    @action(detail=True, methods=['post'], permission_classes=[IsPropertyOwner], url_path='approve')
    def approve_lease(self, request, pk=None):
        """ Landlord approves a PENDING lease request. """
        lease = self.get_object() 
        if lease.status != Lease.LeaseStatus.PENDING:
            return Response({'detail': 'Lease is not in Pending state.'}, status=status.HTTP_400_BAD_REQUEST)
        lease.status = Lease.LeaseStatus.ACTIVE
        lease.save()
        lease.property.availability_status = Property.AvailabilityStatus.RENTED
        lease.property.save()
        serializer = self.get_serializer(lease)
        return Response(serializer.data)


    @action(detail=True, methods=['post'], permission_classes=[IsPropertyOwner], url_path='reject')
    def reject_lease(self, request, pk=None):
        """ Landlord rejects a PENDING lease request. """
        lease = self.get_object()
        if lease.status != Lease.LeaseStatus.PENDING:
            return Response({'detail': 'Lease is not in Pending state.'}, status=status.HTTP_400_BAD_REQUEST)
        lease.status = Lease.LeaseStatus.REJECTED
        lease.save() 
        serializer = self.get_serializer(lease)
        return Response(serializer.data)

    
    @action(detail=True, methods=['post'], permission_classes=[IsPropertyOwner], url_path='complete')
    def complete_lease(self, request, pk=None):
        """ Landlord marks an ACTIVE lease as Completed (e.g., after move-out). """
        lease = self.get_object()
        if lease.status != Lease.LeaseStatus.ACTIVE:
            return Response({'detail': 'Only active leases can be marked as completed.'}, status=status.HTTP_400_BAD_REQUEST)
        lease.status = Lease.LeaseStatus.COMPLETED
        lease.save()
        lease.property.availability_status = Property.AvailabilityStatus.AVAILABLE
        lease.property.save()
        serializer = self.get_serializer(lease)
        return Response(serializer.data)


class ReviewViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing Reviews, nested under a Lease.
    Accessed via /api/v1/leases/{lease_pk}/reviews/
    - Only the Tenant of the *completed* lease can create/update/delete their review.
    - Others involved might be allowed to view (adjust permissions).
    """
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticated] 

    def get_lease(self):
        """Helper method to get the Lease object from URL kwargs."""
        lease_pk = self.kwargs.get('lease_pk')
        if not lease_pk:
            raise NotFound("Lease primary key not found in URL.")     
        lease = get_object_or_404(Lease.objects.select_related('tenant', 'property'), pk=lease_pk)
        return lease

    def get_queryset(self):
        """
        Return reviews only for the specific lease identified in the URL.
        Ensure user has permission to view the lease first.
        """
        lease = self.get_lease()
        user = self.request.user
        if lease.tenant != user and lease.property.owner != user:
             raise PermissionDenied("You do not have permission to view reviews for this lease.")
        return Review.objects.select_related('reviewer__profile').filter(lease=lease)

    def get_serializer_context(self):
        """
        Pass 'request' and 'lease' objects to the serializer context for validation.
        """
        context = super().get_serializer_context()
        context['request'] = self.request
        context['lease'] = self.get_lease()
        return context

    def perform_create(self, serializer):
        """
        Set the reviewer to the current user and link to the lease from the URL.
        Validation happens in the serializer using the context.
        """
        lease = self.get_lease()
        serializer.save(reviewer=self.request.user, lease=lease)

    def perform_update(self, serializer):
        """ Ensure only the reviewer can update their review. """
        review = self.get_object() 
        if review.reviewer != self.request.user:
            raise PermissionDenied("You can only update your own review.")
        serializer.save()

    def perform_destroy(self, instance):
        """ Ensure only the reviewer can delete their review. """
        if instance.reviewer != self.request.user:
             raise PermissionDenied("You can only delete your own review.")
        instance.delete()