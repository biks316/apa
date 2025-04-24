from django.urls import path
from . import views

urlpatterns = [
    path('dash/', views.home, name='home'),  # Root route for your app
]