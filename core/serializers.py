from djoser.serializers import UserCreateSerializer, UserSerializer


class CustomUserCreateSerializer(UserCreateSerializer):

    class Meta(UserCreateSerializer.Meta):
        fields = ["id", "username", "password", "email", "first_name", "last_name"]


class CustomUserSerializer(UserSerializer):
    class Meta(UserSerializer.Meta):
        fields = ["id", "username", "email", "first_name", "last_name"]
