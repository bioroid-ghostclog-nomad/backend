from rest_framework import serializers
from .models import Chating, ChatingRoom
from django.db.models import Sum


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


class StatsSerializer(serializers.ModelSerializer):

    class Meta:
        model = ChatingRoom
        exclude = ("user", "pdf", "pdf_embedding")

    messages_num = serializers.SerializerMethodField()
    conversation_num = serializers.SerializerMethodField()
    file_num = serializers.SerializerMethodField()

    costs = serializers.SerializerMethodField()
    tokens = serializers.SerializerMethodField()

    def get_messages_num(self, chatingroom):
        return chatingroom.chating.count()

    def get_conversation_num(self, chatingroom):
        request = self.context.get("request")
        user = request.user
        return ChatingRoom.objects.filter(user=user).count()

    def get_file_num(self, chatingroom):
        request = self.context.get("request")
        user = request.user
        return ChatingRoom.objects.filter(user=user).count()

    def get_costs(self, chatingroom):
        return chatingroom.chating.aggregate(Sum("cost"))

    def get_tokens(self, chatingroom):
        return chatingroom.chating.aggregate(
            Sum("total_tokens"), Sum("input_tokens"), Sum("output_tokens")
        )
