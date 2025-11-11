from rest_framework.views import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication
from atomicloops.renderers import AtomicJsonRenderer
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken, OutstandingToken


# Logout View
class LogoutView(APIView):

    def post(self, request):
        try:
            if "refresh" not in request.data:
                return Response({"detail": "refresh token is required."}, status=status.HTTP_400_BAD_REQUEST)
            # if "userId" not in request.data:
            #     return Response({"detail": "userId is required."}, status=status.HTTP_400_BAD_REQUEST)

            # Black list token
            refresh_token = request.data["refresh"]
            token = RefreshToken(refresh_token)
            token.blacklist()

            return Response(status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            # print("Error", str(e), flush=True)
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)


# Logout ALL View
class LogoutAllView(APIView):
    permission_classes = [IsAuthenticated,]
    authentication_classes = [JWTAuthentication,]
    renderer_classes = [AtomicJsonRenderer]

    def post(self, request):
        tokens = OutstandingToken.objects.filter(user_id=request.user.id)
        for token in tokens:
            t, _ = BlacklistedToken.objects.get_or_create(token=token)

        return Response(status=status.HTTP_205_RESET_CONTENT)
