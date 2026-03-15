"""
URL configuration for project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
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
from django.urls import path
from app.views import test_view, upload_audio
from app import views
from django.http import Http404
urlpatterns = [
    path('admin/', admin.site.urls),
    #path('', test_view),
    #path('upload_audio/', upload_audio, name = 'upload_audio'),
    path('', views.profile, name='profile'),  # корень приложения — профиль (после логина)
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', views.CustomLogoutView.as_view(), name='logout'),
    path('profile/', views.profile, name='profile'),
    path('analytics/', views.analytics, name='analytics'),
    path('upload/', views.upload_test, name='upload_test'),
    path('create_user/', views.create_user, name='create_user'),
    path('users/', views.user_list, name='user_list'),
]
