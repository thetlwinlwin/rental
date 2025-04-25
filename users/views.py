from django.contrib.auth.models import User
from rest_framework import generics, permissions, viewsets

from .serializers import CurrentUserProfileUpdateSerializer, UserSerializer


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.select_related('profile').filter(is_active=True)
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAdminUser] 


class CurrentUserView(generics.RetrieveUpdateAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return UserSerializer
        return UserSerializer 

class CurrentUserProfileView(generics.RetrieveUpdateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = CurrentUserProfileUpdateSerializer 

    def get_object(self):
        return self.request.user.profile

    
    
    
    