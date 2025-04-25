from rest_framework import permissions, viewsets

from .models import CityDistrict, RegionState, Township
from .serializers import (
    CityDistrictSerializer,
    RegionStateSerializer,
    TownshipSerializer,
)


class RegionStateViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = RegionState.objects.all()
    serializer_class = RegionStateSerializer
    permission_classes = [permissions.AllowAny] 

class CityDistrictViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = CityDistrict.objects.select_related('region_state').all()
    serializer_class = CityDistrictSerializer
    permission_classes = [permissions.AllowAny] 
    

class TownshipViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Township.objects.select_related('city_district__region_state').all()
    serializer_class = TownshipSerializer
    permission_classes = [permissions.AllowAny] 
    