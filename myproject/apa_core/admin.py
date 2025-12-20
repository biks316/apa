from django.contrib import admin
from .models import Embedding

@admin.register(Embedding)
class EmbeddingAdmin(admin.ModelAdmin):
    list_display = ('id', 'topic', 'prompt','value','match_with','get_embedding_preview', 'created_at')
    readonly_fields = ('embedding',)

    def get_embedding_preview(self, obj):
        # Show first few bytes or length for clarity
        return f"{len(obj.embedding)} bytes" if obj.embedding else "None"
    get_embedding_preview.short_description = "Embedding (preview)"