from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.
class User(AbstractUser):
    # 비활성화 컬럼
    first_name = models.CharField(max_length=150, editable=False)
    last_name = models.CharField(max_length=150, editable=False)
    
    # 추가 컬럼
    api_key = models.CharField(max_length=500,blank=True,default=None,null=True)

    def __str__(self):
        return self.username
    
    def have_api(self):
        if self.api_key:
            return "yes"
        return "no"
    
# 이메일 비밀번호 인증용 모델
class EmailValidate(models.Model):
    email = models.EmailField(max_length=254,unique=True)
    code = models.CharField(max_length=8)