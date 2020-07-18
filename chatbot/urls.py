"""chatbot URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
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
from django.conf.urls import url
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView

from chatbot import settings
from chatbot.views import ChatterBotAppView, ChatterBotApiView, ChatterBotApiUpload

urlpatterns = [
    url(r'^$', ChatterBotAppView.as_view(), name='main'),
    url(r'^admin/', admin.site.urls, name='admin'),
    url(r'^api/chatbot/', ChatterBotApiView.as_view(), name='chatbot'),
    url(r'^api/upload/image', ChatterBotApiUpload.as_view(), name='chatbot-upload-img'),
    url(r'^search/', include('haystack.urls')),
    path('ckeditor/', include('ckeditor_uploader.urls')),
    url(r'^favicon.ico$', RedirectView.as_view(url=r'static/img/favicon.ico'))
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
