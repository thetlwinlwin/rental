from django.shortcuts import get_object_or_404
from django_filters import rest_framework as filters
from rest_framework import permissions, viewsets
from rest_framework.exceptions import NotFound, PermissionDenied
from rest_framework.filters import SearchFilter

from .models import Amenity, Property, PropertyImage, PropertyType
from .serializers import (
    AmenitySerializer,
    BulkPropertyImageSerializer,
    PropertyImageSerializer,
    PropertySerializer,
    PropertyTypeSerializer,
)


class PropertyFilter(filters.FilterSet):
    min_price = filters.NumberFilter(field_name="price_per_month", lookup_expr='gte')
    max_price = filters.NumberFilter(field_name="price_per_month", lookup_expr='lte')
    bedrooms = filters.NumberFilter(field_name="bedrooms", lookup_expr='gte')
    property_type = filters.CharFilter(field_name="property_type__name", lookup_expr='iexact')
    township = filters.CharFilter(field_name="township__name", lookup_expr='iexact')
    is_furnished = filters.BooleanFilter(field_name="is_furnished")
    parking_type = filters.CharFilter(field_name="parking_type")

    class Meta:
        model = Property
        fields = []

class PropertyViewSet(viewsets.ModelViewSet):
    serializer_class = PropertySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [filters.DjangoFilterBackend, SearchFilter]
    filterset_class = PropertyFilter
    search_fields = [
        'title', 
        'description',
        'address_line_1',
        'address_line_2',
        'property_type__name',
        'township__name',
        'township__city_district__name',
        'amenities__name'
    ]
    
    def get_queryset(self):
        queryset = Property.objects.select_related(
            'owner', 'property_type', 'township__city_district__region_state'
        ).prefetch_related('amenities', 'images').all()

        
        ordering = self.request.query_params.get('ordering')
        if ordering:
            queryset = queryset.order_by(ordering)
        return queryset

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

class PropertyTypeViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = PropertyType.objects.all()
    serializer_class = PropertyTypeSerializer
    permission_classes = [permissions.AllowAny]

class AmenityViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Amenity.objects.all()
    serializer_class = AmenitySerializer
    permission_classes = [permissions.AllowAny] 

class PropertyImageViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_property(self):
        property_pk = self.kwargs.get('property_pk')
        if not property_pk:
            raise NotFound("Property key not found in URL.")
        return get_object_or_404(Property.objects.all(), pk=property_pk)

    def get_queryset(self):
        return PropertyImage.objects.filter(
            property=self.get_property()
        ).order_by('order')

    def get_serializer_class(self):
        if self.action == 'create':
            return BulkPropertyImageSerializer
        return PropertyImageSerializer

    def perform_create(self, serializer):
        property_obj = self.get_property()
        if property_obj.owner != self.request.user:
            raise PermissionDenied("Cannot add images to properties you don't own.")
        
        if isinstance(serializer, BulkPropertyImageSerializer):
            serializer.save()
        else:
            serializer.save(property=property_obj)

    def perform_update(self, serializer):
        if serializer.instance.property.owner != self.request.user:
            raise PermissionDenied("Cannot modify images on properties you don't own.")
        serializer.save()

    def perform_destroy(self, instance):
        if instance.property.owner != self.request.user:
            raise PermissionDenied("Cannot delete images from properties you don't own.")
        instance.delete()

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['property'] = self.get_property()
        return context