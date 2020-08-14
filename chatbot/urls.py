from django.conf.urls import url
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView

from chatbot import settings
from chatbot.view.chatbot_views import ChatterBotAppView, ChatterBotApiView, ChatterBotApiUpload
from chatbot.view.spider_views import Spider, FAQSpider

urlpatterns = [
    url(r'^$', ChatterBotAppView.as_view(), name='main'),
    url(r'^admin/', admin.site.urls, name='admin'),
    url(r'^api/chatbot/', ChatterBotApiView.as_view(), name='chatbot'),
    url(r'^api/upload/image', ChatterBotApiUpload.as_view(), name='chatbot-upload-img'),
    url(r'^search/', include('haystack.urls')),
    path('ckeditor/', include('ckeditor_uploader.urls')),
    url(r'^favicon.ico$', RedirectView.as_view(url=r'static/img/favicon.ico')),
    url(r'^spider$', Spider.as_view(), name='spider'),
    url(r'^api/spider/', FAQSpider.as_view(), name='spider')
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
