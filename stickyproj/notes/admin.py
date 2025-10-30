from django.contrib import admin
from .models import Note


@admin.register(Note)
class NoteAdmin(admin.ModelAdmin):
    list_display = ('title', 'timestamp')
    search_fields = ('title', 'content')
    ordering = ('-timestamp',)
