from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("view/", views.view, name="index"),
    path("home/", views.home, name="home"),
    path("create/", views.get_name, name="index"),
    path("<int:id>", views.index, name="index"),
    path('upload_file/', views.upload_file, name='upload_file'),
    path('process_audio/', views.process_audio, name='process_audio'),
    path('generate_ai_audio/', views.generate_ai_audio, name='generate_ai_audio'),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
