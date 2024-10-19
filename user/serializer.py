from rest_framework import serializers
from .models import User


# 유저 등록시에 사용되는 시리얼라이저 / 객체 생성 단계에서 비밀번호를 해싱하게 설정
class UserRegistSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("username", "password", "email")

    def create(self, validated_data):
        user = User(
            username=validated_data["username"],
            email=validated_data["email"],
        )
        user.set_password(validated_data["password"])
        user.save()
        return user

# 단순 유저 시리얼라이저
class TinyUserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = (
            "username",
            "email",
        )