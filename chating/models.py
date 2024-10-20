from django.db import models

# Create your models here.
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

class Chating(models.Model):
    chatingRoom = models.ForeignKey(
        ChatingRoom,
        on_delete=models.CASCADE,
        related_name="Chating",
    )
    chat = models.TextField()
    speaker = models.CharField(max_length=30)