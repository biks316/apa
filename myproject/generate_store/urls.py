from django.urls import path
from . import views

app_name = "generate_store"

urlpatterns = [
    # Simple sample endpoints that call into views. Replace or extend these
    # with your real endpoints as needed.
    # path("", views.index, name="index"),
    path("fetch/", views.fetch_item, name="fetch_item"),
    path("documents/", views.list_documents, name="list_documents"),
    path("autocomplete/", views.autocomplete_suggestions, name="autocomplete_suggestions"),
    # path("documents/", views.list_documents, name="list_documents"),
    # path("documents/<int:pk>/", views.document_detail, name="document_detail"),
]

