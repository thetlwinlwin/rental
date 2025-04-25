from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register(r'leases', views.LeaseViewSet, basename='lease')

review_list = views.ReviewViewSet.as_view({
    'get': 'list',
    'post': 'create'
})

review_detail = views.ReviewViewSet.as_view({
    'get': 'retrieve',
    'put': 'update',
    'patch': 'partial_update',
    'delete': 'destroy'
})

urlpatterns = [
    path('', include(router.urls)),
    path('leases/<int:lease_pk>/reviews/', review_list, name='lease-review-list'),
    path('leases/<int:lease_pk>/reviews/<int:pk>/', review_detail, name='lease-review-detail'),
]