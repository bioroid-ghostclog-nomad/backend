# 파이썬 모듈
import secrets  # 인증 코드 생성용

# Django 기본 제공
from django.contrib.auth import authenticate, login, logout
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.conf import settings
from django.core import signing

# 프로젝트 내에서 정의한 내영
from .models import User, EmailValidate
from .serializer import TinyUserSerializer, UserRegistSerializer

# DRF
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST, HTTP_201_CREATED, HTTP_404_NOT_FOUND
from rest_framework.exceptions import NotFound, ParseError, PermissionDenied
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly

# 랭체인
from langchain_openai import ChatOpenAI

# Create your views here.


class Me(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        serializer = TinyUserSerializer(user)
        return Response(serializer.data)

    def put(self, request):
        user = request.user
        serializer = TinyUserSerializer(
            user,
            data=request.data,
            partial=True,
        )
        if serializer.is_valid():
            updated_user = serializer.save()
            return Response(
                TinyUserSerializer(updated_user).data,
            )
        else:
            return Response(
                serializer.errors,
                status=HTTP_400_BAD_REQUEST,
            )


class UserPassword(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        password = request.data.get("password")
        if not password:
            raise ParseError
        if user.check_password(password):
            return Response(status=HTTP_200_OK)
        else:
            raise PermissionDenied

    def put(self, request):
        user = request.user
        old_password = request.data.get("old_password")
        new_password = request.data.get("new_password")
        if not old_password or not new_password:
            raise ParseError
        if user.check_password(old_password):
            user.set_password(new_password)
            user.save()
            return Response(status=HTTP_200_OK)
        else:
            raise PermissionDenied


class UserData(APIView):
    def post(self, request):
        serializer = UserRegistSerializer(data=request.data)
        if serializer.is_valid():  # 데이터 유효성 검사
            user = serializer.save()
            serializer = UserRegistSerializer(user)
            return Response(serializer.data, status=HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)


# 아이디 중복 체크
class IdChk(APIView):
    def post(self, request):
        username = request.data.get("username")
        if User.objects.filter(username=username).exists():
            return Response({"response": "중복 아이디입니다."})
        return Response({"response": "사용 가능한 아이디입니다."})


# 이메일 검증
class Email(APIView):
    def get_object(self, email):
        try:
            return EmailValidate.objects.get(email=email)
        except:
            return None

    def post(self, request):  # 인증 메일 발송
        email = request.data.get("email")
        code = str(secrets.randbelow(1000000)).zfill(6)  # 6자리 인증 코드 생성
        email_obj = self.get_object(email=email)
        if email_obj:  # 이미 인증 메일을 보낸 이메일의 경우(객체 덮어쓰기)
            email_obj.code = code
            email_obj.save()
        else:  # 처음으로 인증 메일을 보내는 경우(데이터 생성)
            email_obj = EmailValidate.objects.create(email=email, code=code)
        context = {  # 사용자에게 보낼 이메일 내용 설정
            "username": email,  # 사용자 이름을 이메일로 대체 (실제 사용자 이름이 있다면 변경)
            "verification_code": code,
        }
        html_content = render_to_string("sendmail.html", context)  # HTML 템플릿 렌더링
        email_message = EmailMessage(
            subject="Your Email Verification Code",  # 이메일 제목
            body=html_content,  # HTML 내용
            from_email=settings.DEFAULT_FROM_EMAIL,  # 발신자 이메일
            to=[email],  # 수신자 이메일
        )
        email_message.content_subtype = "html"  # 이메일 형식을 HTML로 설정
        email_message.send()  # 이메일 발송
        return Response({"response": "이메일이 발송되었습니다."}, status=200)

    def delete(self, request):  # 이메일 검증 및 검증 성공한 모델 제거
        email = request.data.get("email")
        code = request.data.get("code")
        try:
            email_obj = EmailValidate.objects.get(email=email, code=code)
            email_obj.delete()
            return Response({"response": "success"})
        except:
            return Response({"response": "fail"})

class APIKey(APIView):
    permission_classes = [IsAuthenticated]

        
    def get(self, request):
        user = request.user
        if user.api_key:
            return Response({"response": "success"}, status=HTTP_200_OK)
        return Response({"response": "fail"}, status=HTTP_404_NOT_FOUND)

    def post(self, request):
        user = request.user
        api_key = request.data.get("api_key")
        llm = ChatOpenAI(
            temperature=0,
            openai_api_key=api_key,
        )
        try:
            llm.predict("안녕") # 유효하지 않은 api키면 에러 발생.
            user.api_key = signing.dumps(api_key)
            user.save()
            return Response({"response": "등록 성공!"}, status=HTTP_201_CREATED)
        except:
            return Response({"response": "유효하지 않은 API키입니다!"}, status=HTTP_400_BAD_REQUEST)


        


### jwt 방식으로 인해 하단의 비지니스 코드들은 사용하지 않습니다. ###
class Login(APIView):
    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")
        if not username or not password:
            raise ParseError
        user = authenticate(
            request,
            username=username,
            password=password,
        )
        if user:
            login(request, user)
            return Response(
                {"response": f"로그인 성공! 어서오세요. {user.username}님!"},
                status=HTTP_200_OK,
            )
        else:
            return Response(
                {"response": "로그인 실패. 아이디 혹은 비밀번호를 재확인해주세요."},
                status=HTTP_400_BAD_REQUEST,
            )


# 로그아웃
class Logout(APIView):
    # 권한 체크. 상식적으로 로그인 안된 유저가 로그아웃을 할 수 있을리가 없잖아요?
    permission_classes = [IsAuthenticated]

    def post(self, request):
        logout(request)
        return Response({"response": "로그아웃 되었습니다!"})
