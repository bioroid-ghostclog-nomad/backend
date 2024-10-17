# Django 기본 제공
from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout
# 프로젝트 내에서 정의한 내영
from .models import User
from .serializer import UserRegistSerializer
# DRF
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK,HTTP_400_BAD_REQUEST,HTTP_201_CREATED
from rest_framework.exceptions import NotFound,ParseError,PermissionDenied
from rest_framework.permissions import IsAuthenticated,IsAuthenticatedOrReadOnly
# Create your views here.

class Regist(APIView):
    def post(self,request):
        serializer = UserRegistSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            serializer = UserRegistSerializer(user)
            return Response(serializer.data,status=HTTP_201_CREATED)
        else:
            return Response(serializer.errors,status=HTTP_400_BAD_REQUEST)
        
class Login(APIView):
    def post(self,request):
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
            return Response({"response": f"로그인 성공! 어서오세요. {user.user_nickname}님!"},status=HTTP_200_OK)
        else:
            return Response({"response": "로그인 실패. 아이디 혹은 비밀번호를 재확인해주세요."},status=HTTP_400_BAD_REQUEST)
        
# 로그아웃
class Logout(APIView):
    # 권한 체크. 상식적으로 로그인 안된 유저가 로그아웃을 할 수 있을리가 없잖아요?
    permission_classes = [IsAuthenticated] 
    def post(self, request):
        logout(request)
        return Response({"response": "로그아웃 되었습니다!"})