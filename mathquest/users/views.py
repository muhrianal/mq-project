from rest_framework.views import APIView
from rest_framework.response import Response
from .models import User
from .serializers import ProfileSerializer

class ProfileView(APIView):
    def get(self, request):
        user = User.objects.get(pk=1)
        ser = ProfileSerializer(user)
        return Response(ser.data)
