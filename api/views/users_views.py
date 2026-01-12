from rest_framework import generics, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from api.serializers.users_serializers import UserSerializer
from users.models import ModuleUser, Role


class UserViewSet(viewsets.ModelViewSet):
    queryset = ModuleUser.active_objects.all()
    serializer_class = UserSerializer
    lookup_field = 'username'
    permission_classes = [IsAuthenticated]

    @action(methods=['GET', 'PATCH'], detail=False)
    def me(self, request):
        user = request.user
        if request.method == 'GET':
            serializer = UserSerializer(user)
            return Response(serializer.data)
        serializer = UserSerializer(user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save(role=user.role, partial=True)
        return Response(serializer.data)
