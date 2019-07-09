from rest_framework.views import APIView
from project_admin.serializers.admin_login import LoginSerializer

from rest_framework.response import Response


# POST /meiduo_admin/authorizations/
class AdminLoginView(APIView):

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data)
