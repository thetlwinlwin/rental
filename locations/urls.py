from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'regions', views.RegionStateViewSet, basename='regionstate')
router.register(r'districts', views.CityDistrictViewSet, basename='citydistrict')
router.register(r'townships', views.TownshipViewSet, basename='township')

urlpatterns = [
    path('', include(router.urls)),
]