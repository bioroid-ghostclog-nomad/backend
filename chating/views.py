# 파이썬 모듈
import json

# Django 기본 제공 기능
from django.core import signing

# 프로젝트 내에서 정의한 내용
from .models import Chating, ChatingRoom
from .serializer import ChatingRoomSerializer, ChatingSerializer

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
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.text_splitter import CharacterTextSplitter
from langchain_community.embeddings import OpenAIEmbeddings
from langchain_unstructured import UnstructuredLoader
from langchain_community.vectorstores import FAISS
from langchain.schema.runnable import RunnablePassthrough, RunnableLambda

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

    def post(self, request):  # PDF 전달받고, 임베딩.
        try:
            # 기본 정보 받아오기 및 기본 객체 생성
            title = request.data.get("title")
            model = request.data.get("model")
            pdf = request.FILES.get("pdf")
            chating_room = ChatingRoom.objects.create(
                user=request.user,
                title=title,
                pdf=pdf,
                ai_model=model,
            )
            chating_room.save()
            pdf_path = chating_room.pdf.path
            # 분할기 객체
            splitter = CharacterTextSplitter.from_tiktoken_encoder(
                separator="\n",
                chunk_size=600,
                chunk_overlap=100,
            )
            # PDF 업로드
            loader = UnstructuredLoader(pdf_path)
            # 업로드 PDF spliter로 분활
            docs = loader.load_and_split(text_splitter=splitter)
            # 사용자 api key로 임베딩 객체 생성
            embeddings = OpenAIEmbeddings(
                openai_api_key=signing.loads(request.user.api_key)
            )
            # 임베딩 객체로 데이터 토크나이저
            embedded_docs = embeddings.embed_documents(
                [doc.page_content for doc in docs]
            )
            # 임베딩 데이터를 Json으로 변환
            chating_room.pdf_embedding = json.dumps(embedded_docs)
            # 인스턴스 완전 저장
            chating_room.save()
            pk = chating_room.pk
            return Response({"response": "success", "pk": pk})
        except Exception as e:
            # print(e.with_traceback())
            return Response({"response": "fail"})


# 메세지
class Messages(APIView):

    permission_classes = [IsAuthenticated]

    def get_history(self):
        all_chats = self.get_chatting_room
        pass

    def format_docs(docs):
        return "\n\n".join(document.page_content for document in docs)

    def get_chatting_room(self, id):
        try:
            return ChatingRoom.objects.get(id=id)
        except ChatingRoom.DoesNotExist:
            raise NotFound("채팅방을 찾지 못했습니다.")

    def get(self, request, id):
        # 채팅방 하나의 모든 채팅 메세지 반환
        chatting_room = self.get_chatting_room(id)
        # 채팅방 소유 여부 확인
        user = request.user

        if user != chatting_room.user:
            raise PermissionDenied("이 채팅방에 접근할 권한이 없습니다.")

        chats = chatting_room.chating

        serializer = ChatingRoomSerializer(chats, many=True)

        return Response(serializer.data)

    def post(self, request, id):
        # 사람과 AI 간의 채팅
        chatting_room = self.get_chatting_room(id)
        user = request.user

        if user != chatting_room.user:
            raise PermissionDenied("이 채팅방에 접근할 권한이 없습니다.")

        human_message = request.data("chat")

        human_message_serializer = ChatingSerializer(data=request.data)
        if human_message_serializer.is_valid():
            human_message_serializer.save(chatingRoom=chatting_room)
            # AI 답변 진행
            pdf_path = chatting_room.pdf.path
            # 분할기 객체
            splitter = CharacterTextSplitter.from_tiktoken_encoder(
                separator="\n",
                chunk_size=600,
                chunk_overlap=100,
            )
            # PDF 업로드
            loader = UnstructuredLoader(pdf_path)
            # 업로드 PDF spliter로 분활
            docs = loader.load_and_split(text_splitter=splitter)

            pdf_embedding = chatting_room.pdf_embedding
            vectorstore = FAISS.from_documents(docs, pdf_embedding)
            retriever = vectorstore.as_retriever()

            llm = ChatOpenAI(
                api_key=user.api_key,
                model=chatting_room.ai_model,
                temperature=0.1,
            )

            prompt = ChatPromptTemplate.from_messages(
                [
                    (
                        "system",
                        """
            Answer the question using ONLY the following context. If you don't know the answer just say you don't know. DON'T make anything up.
            
            Context: {context}
            """,
                    ),
                    MessagesPlaceholder(variable_name="history"),
                    ("human", "{question}"),
                ]
            )

            chain = (
                {
                    "history": RunnableLambda(self.get_history),
                    "context": retriever | RunnableLambda(self.format_docs),
                    "question": RunnablePassthrough(),
                }
                | prompt
                | llm
            )

            result = chain.invoke(human_message)
            ai_message = result.content

            Chating.objects.create(
                chat=ai_message,
                speaker="ai",
                chatingRoom=chatting_room,
            )

            return Response({"ai_message": ai_message})
        else:
            return Response(human_message_serializer.error, status=HTTP_400_BAD_REQUEST)
