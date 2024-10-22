from django.contrib import admin
from .models import Chating, ChatingRoom


# Register your models here.
@admin.register(ChatingRoom)
class ChatingRoomAdmin(admin.ModelAdmin):

    list_display = (
        "user",
        "title",
        "ai_model",
    )

    readonly_fields = (
        "pdf",
        "pdf_embedding",
    )


@admin.register(Chating)
class ChatingAdmin(admin.ModelAdmin):

    list_display = (
        "chatingRoom",
        "chat",
        "speaker",
    )
