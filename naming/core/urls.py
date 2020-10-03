"""naming URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
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
from django.urls import include, path

from . import views

urlpatterns = [
    path("api/hosts/", views.retrieve_storage_servers, name="retrive-storage-servers"),
    path("api/server/register/", views.register_new_storage_server, name="new-server"),
    path("api/file/", views.FileView.as_view(), name="file"),
    path("api/file/approve/", views.file_approve, name="file-approve"),
    path("api/file/delete/", views.file_delete, name="file-delete"),
    path("api/directory/", views.retrieve_storage_servers, name="retrieve-directory-content"),
]
