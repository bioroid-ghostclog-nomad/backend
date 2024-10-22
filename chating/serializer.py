from rest_framework import serializers
from .models import Chating, ChatingRoom


# 채팅룸 시리얼라이저
class ChatingRoomSerializer(serializers.ModelSerializer):

    class Meta:
        model = ChatingRoom
        fields = "__all__"

    def create(self, validated_data):
        # 객체 생성
        chat_room = ChatingRoom(**validated_data)
        chat_room.save()  # 저장 후 pdf_embedding 생성
        return chat_room


class ChatingRoomListSerializer(serializers.ModelSerializer):

    class Meta:
        model = ChatingRoom
        fields = (
            "title",
            "id",
        )

    def create(self, validated_data):
        # 객체 생성
        chat_room = ChatingRoom(**validated_data)
        chat_room.save()  # 저장 후 pdf_embedding 생성
        return chat_room


class ChatingSerializer(serializers.ModelSerializer):

    class Meta:
        model = Chating
        fields = (
            "speaker",
            "chat",
        )
