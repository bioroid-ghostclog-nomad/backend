from django.db import models
import json

class ChatingRoom(models.Model):
    user = models.ForeignKey(
        "user.User",
        on_delete=models.CASCADE,
        related_name="ChatingRoom"
    )
    pdf = models.FileField(upload_to="pdfs/", max_length=100)
    ai_model = models.CharField(
        default="gpt-4o-mini",
        max_length=30
    )
    pdf_embedding = models.JSONField(null=True, blank=True)  # JSONField 사용 / 실제 저장은 문자열로

    def save_pdf_embedding(self, embedding):
        self.pdf_embedding = json.dumps(embedding)  # 임베딩을 JSON으로 저장
        self.save()


class Chating(models.Model):
    chatingRoom = models.ForeignKey(
        ChatingRoom,
        on_delete=models.CASCADE,
        related_name="chating",
    )
    chat = models.TextField()
    speaker = models.CharField(max_length=30)