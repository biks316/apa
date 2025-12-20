from django.urls import path
from . import views

app_name = "apa_core"  # <-- Important for namespacing

urlpatterns = [
    path('create/', views.create_apa_report, name='create_apa_report'),
]