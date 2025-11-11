from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.views import Response
from rest_framework.permissions import AllowAny
from rest_framework import exceptions, status
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken
from django.utils.translation import gettext_lazy as _
from users.models import Users


# Custom Failure Class
class TokenBackendError(Exception):
    pass


class DetailDictMixin:
    def __init__(self, detail=None, code=None):
        """
        Builds a detail dictionary for the error to give more information to API
        users.
        """
        detail_dict = {"detail": self.default_detail, "code": self.default_code}

        if isinstance(detail, dict):
            detail_dict.update(detail)
        elif detail is not None:
            detail_dict["detail"] = detail

        if code is not None:
            detail_dict["code"] = code

        super().__init__(detail_dict)


class AuthenticationFailed(DetailDictMixin, exceptions.AuthenticationFailed):
    pass


class TokenError(Exception):
    pass


class InvalidToken(AuthenticationFailed):
    status_code = status.HTTP_401_UNAUTHORIZED
    default_detail = "Token is invalid or expired"
    default_code = "token_not_valid"


# Add more info to Token
class CustomTokenPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super(TokenObtainPairSerializer, cls).get_token(user)
        return token

    def validate(self, data):
        """
        Check if the user exists.
        """
        try:
            user = Users.objects.get(email=data['email'])
            if user.signInMethod != "email" and user.password is None:
                raise serializers.ValidationError(_("User with email %(email)s is registered with Google SignIn") % {'email': data['email']})
            if not user.is_active:
                raise serializers.ValidationError(_("User with email %(email)s is inactive") % {'email': data['email']})
            if not user.isVerified:
                raise serializers.ValidationError(_("User with email %(email)s is not verified") % {'email': data['email']})
            super().validate(data)
            token = RefreshToken.for_user(user)
            data = dict()
            data['refresh'] = str(token)
            data['access'] = str(token.access_token)
            return data
        except Users.DoesNotExist:
            raise serializers.ValidationError(_("User with email %(email)s does not exist") % {'email': data['email']})


# Add more info to Token
class AdminCustomTokenPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super(TokenObtainPairSerializer, cls).get_token(user)
        return token

    def validate(self, data):
        """
        Check if the user exists.
        """
        try:
            user = Users.objects.get(email=data['email'])
            if user.signInMethod != "email" and user.password is None:
                raise serializers.ValidationError(_("User with email %(email)s is registered with Google SignIn") % {'email': data['email']})
            if not user.is_active:
                raise serializers.ValidationError(_("User with email %(email)s is inactive") % {'email': data['email']})
            if not user.isVerified:
                raise serializers.ValidationError(_("User with email %(email)s is not verified") % {'email': data['email']})
            if not user.is_superuser:
                raise serializers.ValidationError(f"User with email {data['email']} is not admin")
            if not user.level == 5:
                raise serializers.ValidationError(f"User with email {data['email']} is not admin")

            super().validate(data)
            token = RefreshToken.for_user(user)
            data = dict()
            data['refresh'] = str(token)
            data['access'] = str(token.access_token)
            return data
        except Users.DoesNotExist:
            raise serializers.ValidationError(_("User with email %(email)s does not exist") % {'email': data['email']})


# Get Token View
class LoginView(TokenObtainPairView):
    """
    Takes email and password as input  and returns an access type JSON web
    token and a refresh type JSON web token
    """
    permission_classes = (AllowAny,)
    authentication_classes = ()
    serializer_class = CustomTokenPairSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
        except TokenError as e:
            raise InvalidToken(e.args[0])
        return Response(serializer.validated_data, status=status.HTTP_200_OK)


# Get Token View
class AdminLoginView(TokenObtainPairView):
    """
    Takes email and password as input  and returns an access type JSON web
    token and a refresh type JSON web token.
    This view is only for admin users
    """
    permission_classes = (AllowAny,)
    authentication_classes = ()
    serializer_class = AdminCustomTokenPairSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
        except TokenError as e:
            raise InvalidToken(e.args[0])
        return Response(serializer.validated_data, status=status.HTTP_200_OK)

# class RefreshTokenView(TokenRefreshView):
#     # permission_classes = (AllowAny,)
#     # authentication_classes = ()
#     # serializer_class = TokenRefreshSerializer
#     # renderer_classes = [AtomicJsonRenderer]

#     # def post(self, request, *args, **kwargs):
#     #     serializer = self.serializer_class(data=request.data)
#     #     try:
#     #         serializer.is_valid(raise_exception=True)
#     #     except TokenError as e:
#     #         raise InvalidToken(e.args[0])
#     #     # obj =  User.objects.filter(email=request.data['email']).first()
#     #     # serializer.validated_data['email'] = obj.email
#     #     # serializer.validated_data['id'] = obj.id
#     #     # serializer.validated_data['firstName'] = obj.firstName
#     #     return Response(serializer.validated_data, status=status.HTTP_200_OK)
