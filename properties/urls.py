from django.urls import include, path
from rest_framework_nested import routers

from . import views

router = routers.SimpleRouter()
router.register(r'properties', views.PropertyViewSet, basename='property')
router.register(r'property-types', views.PropertyTypeViewSet, basename='propertytype')
router.register(r'amenities', views.AmenityViewSet, basename='amenity')

properties_router = routers.NestedSimpleRouter(router, r'properties', lookup='property')
properties_router.register(r'images', views.PropertyImageViewSet, basename='property-image')

urlpatterns = [
    path('', include(router.urls)),
    path('', include(properties_router.urls)), 
]