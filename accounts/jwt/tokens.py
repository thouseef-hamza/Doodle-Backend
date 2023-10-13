from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import RefreshToken


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = RefreshToken.for_user(user)

        token["email"] = user.email
        token["is_blocked"] = user.is_blocked
        token["is_institute"] = user.is_institute
        token["is_teacher"] = user.is_teacher
        token["is_student"] = user.is_student

        return token
