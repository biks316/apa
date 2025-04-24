"""
URL configuration for myproject project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

# from django.contrib import admin
# from django.urls import path

# urlpatterns = [
#     path("admin/", admin.site.urls),
# ]


from django.contrib import admin
from . import views
from django.urls import path, include  # 👈 include is needed

urlpatterns = [
    path('admin/', admin.site.urls),
    path('app/', include('dash.urls')),
   path('dash/', views.home, name='home'),  # Root route for your app
   path('gantt/', views.gantt, name='gantt'), 
   path('welcome/', views.welcome, name='welcome'), 
   path('', views.create_apa_report, name='create_apa_report'),    
]