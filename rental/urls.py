from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),

    # API endpoints
    path('api/v1/', include('locations.urls')),
    path('api/v1/', include('properties.urls')),
    path('api/v1/', include('leases.urls')),
    path('api/v1/', include('users.urls')),


    # dj-rest-auth registration URLs
    path('api/v1/auth/registration/', include('dj_rest_auth.registration.urls')), 

    # dj-rest-auth URLs for other authentication actions (login, logout, etc.)
    path('api/v1/auth/', include('dj_rest_auth.urls')), 
]

# Development media serving
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)