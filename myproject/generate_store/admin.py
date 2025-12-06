from django.contrib import admin
from .models import Topic, FetchedDocument, RichContent


@admin.register(RichContent)
class RichContentAdmin(admin.ModelAdmin):
	list_display = ("title", "topic", "created_at")
	search_fields = ("title", "excerpt")


admin.site.register(Topic)
admin.site.register(FetchedDocument)
