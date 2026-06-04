from django.contrib import admin
from .models import Message

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display  = ['sender', 'team', 'text', 'deleted', 'created_at']
    list_filter   = ['deleted', 'team']
    search_fields = ['text', 'sender__username']
