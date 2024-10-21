# 파이썬 모듈
from io import BytesIO
import json

# Django 기본 제공
from django.core import signing

# 프로젝트 내에서 정의한 내영
from .models import Chating, ChatingRoom
from .serializer import ChatingRoomSerializer

# DRF
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.status import (
    HTTP_200_OK,
    HTTP_400_BAD_REQUEST,
    HTTP_201_CREATED,
    HTTP_404_NOT_FOUND,
)
from rest_framework.exceptions import NotFound, ParseError, PermissionDenied
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly

# 랭체인
from langchain_openai import ChatOpenAI
from langchain.text_splitter import CharacterTextSplitter
from langchain_community.embeddings import OpenAIEmbeddings
from langchain_unstructured import UnstructuredLoader

# 기타 모듈


class ChatingRooms(APIView):
    permission_classes = [IsAuthenticated]


class ChatingRoomData(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, pk):
        try:
            return ChatingRoomSerializer(ChatingRoom.objects.get(pk=pk))
        except:
            raise NotFound

    def get(self, request):
        pk = request.data.get("pk")
        serializer = self.get_object(pk=pk)
        return Response(serializer.data, status=HTTP_200_OK)

    def post(self, request):
        try:
            title = request.data.get("title")
            model = request.data.get("model")
            pdf = request.FILES.get("pdf")
            chating_room = ChatingRoom.objects.create(
                user=request.user,  # 또는 필요한 사용자 지정
                pdf=pdf,
                ai_model=model,
            )
            chating_room.save()
            pk = chating_room.pk
            pdf_path = chating_room.pdf.path

            splitter = CharacterTextSplitter.from_tiktoken_encoder(
                separator="\n",
                chunk_size=600,
                chunk_overlap=100,
            )
            loader = UnstructuredLoader(pdf_path)
            docs = loader.load_and_split(text_splitter=splitter)
            embeddings = OpenAIEmbeddings(openai_api_key = signing.loads(request.user.api_key))
            embedded_docs = embeddings.embed_documents([doc.page_content for doc in docs])
            # 임베딩을 JSON으로 저장
            chating_room.pdf_embedding = json.dumps(embedded_docs)
            # 인스턴스 저장
            chating_room.save()
            return Response({"response": "success", "pk": pk})
        except:
            return Response({"response": "fail", "pk": pk})


class Messages(APIView):

    def get_chatting_room(self, id):
        try:
            return ChatingRoom.objects.get(id=id)
        except ChatingRoom.DoesNotExist:
            raise NotFound("채팅방을 찾지 못했습니다.")

    def get(self, request, id):
        # 채팅방 하나의 모든 채팅 메세지 반환
        chatting_room = self.get_chatting_room(id)
        user = request.user

        if user != chatting_room.user:
            raise PermissionDenied("이 채팅방에 접근할 권한이 없습니다.")

        chats = chatting_room.chating

        serializer = ChatingRoomSerializer(chats, many=True)

        return Response(serializer.data)
