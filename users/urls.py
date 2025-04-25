from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()


urlpatterns = [
    path('', include(router.urls)),
    path('users/me/', views.CurrentUserView.as_view(), name='current-user'),
    path('users/me/profile/', views.CurrentUserProfileView.as_view(), name='current-user-profile'),
]