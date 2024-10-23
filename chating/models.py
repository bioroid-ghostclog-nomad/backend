from django.db import models


class ChatingRoom(models.Model):
    user = models.ForeignKey(  # 채팅방 소유 유저
        "user.User", 
        on_delete=models.CASCADE, 
        related_name="ChatingRoom"
    )
    title = models.CharField(
        max_length=30, 
        default="(Chatting Room Title)")
    pdf = models.FileField(
        upload_to="pdfs/", 
        max_length=100)  # 사용할 PDF
    ai_model = models.CharField(  # 사용할 llm 모델. 기본값은 '4 mini'
        default="gpt-4o-mini", 
        max_length=30
    )
    pdf_embedding = models.JSONField(
        null=True, blank=True
    )  # JSONField 사용 / 실제 저장은 문자열로 / PDF 임베딩


class Chating(models.Model):
    chatingRoom = models.ForeignKey(
        ChatingRoom,
        on_delete=models.CASCADE,
        related_name="chating",
    )
    chat = models.TextField()  # 채팅 내용
    speaker = models.CharField(max_length=30)  # 화자
