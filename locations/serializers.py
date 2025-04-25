from rest_framework import serializers

from .models import CityDistrict, RegionState, Township


class RegionStateSerializer(serializers.ModelSerializer):
    class Meta:
        model = RegionState
        fields = ['id', 'name', 'slug']

class CityDistrictSerializer(serializers.ModelSerializer):
    region_state_name = serializers.CharField(source='region_state.name', read_only=True)

    class Meta:
        model = CityDistrict
        fields = ['id', 'name', 'slug', 'region_state', 'region_state_name']
        read_only_fields = ['region_state_name'] 

class TownshipSerializer(serializers.ModelSerializer):
    city_district_name = serializers.CharField(source='city_district.name', read_only=True)
    region_state_name = serializers.CharField(source='city_district.region_state.name', read_only=True)

    class Meta:
        model = Township
        fields = ['id', 'name', 'slug', 'city_district', 'city_district_name', 'region_state_name']
        read_only_fields = ['city_district_name', 'region_state_name']