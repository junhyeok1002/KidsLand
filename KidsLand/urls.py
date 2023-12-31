"""
URL configuration for KidsLand project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
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
from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView

from user.views import Main

from .settings import MEDIA_URL, MEDIA_ROOT
from django.conf.urls.static import static
from .views import splash_view

urlpatterns = [
    path("admin/", admin.site.urls),
    # path('', RedirectView.as_view(url='main/', permanent=False)),
    path('', splash_view),
    path('main/', Main.as_view()),
    path('user/', include('user.urls')),
]

urlpatterns += static(MEDIA_URL, document_root=MEDIA_ROOT)
